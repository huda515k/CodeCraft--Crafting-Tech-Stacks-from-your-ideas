"""
Gemini Wrapper - Supports both direct API and Gemini CLI
Allows seamless switching between API and CLI without changing app architecture
"""
import asyncio
import json
import base64
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import google.generativeai as genai


class GeminiWrapper:
    """
    Wrapper that supports both Gemini API and Gemini CLI
    Automatically uses CLI if available and configured, falls back to API
    """
    
    def __init__(self, api_key: Optional[str] = None, use_cli: Optional[bool] = None, model: str = "gemini-2.5-flash"):
        """
        Initialize Gemini wrapper
        
        Args:
            api_key: Gemini API key (required if use_cli=False)
            use_cli: Force use CLI (True) or API (False). If None, auto-detect
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Auto-detect if CLI is available
        if use_cli is None:
            self.use_cli = self._check_cli_available()
        else:
            self.use_cli = use_cli
        
        # Initialize API client if not using CLI
        if not self.use_cli:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY required when not using CLI")
            genai.configure(api_key=self.api_key)
            # Map model names for API compatibility
            api_model = self._map_model_for_api(self.model)
            self.model_instance = genai.GenerativeModel(api_model)
        else:
            # Still configure API as fallback for images if API key is provided
            if self.api_key and self.api_key != "dummy-key-for-cli":
                try:
                    genai.configure(api_key=self.api_key)
                    api_model = self._map_model_for_api(self.model)
                    self.model_instance = genai.GenerativeModel(api_model)
                except:
                    self.model_instance = None
            else:
                self.model_instance = None
            print("✅ Using Gemini CLI (better quotas with OAuth)")
    
    def _check_cli_available(self) -> bool:
        """Check if Gemini CLI is installed and available"""
        try:
            result = subprocess.run(
                ["gemini", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _map_model_for_api(self, model: str) -> str:
        """Map CLI model names to API model names"""
        # Use gemini-flash-latest directly for API (as user requested)
        model_mapping = {
            "gemini-2.5-pro": "gemini-flash-latest",  # Fallback to flash-latest
            "gemini-2.5-flash": "gemini-flash-latest",
            "gemini-2.5-flash-lite": "gemini-flash-latest",
            "gemini-3-pro-preview": "gemini-flash-latest",
            "gemini-flash-latest": "gemini-flash-latest",  # Use directly
        }
        return model_mapping.get(model, "gemini-flash-latest")  # Default to gemini-flash-latest
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text response from prompt"""
        if self.use_cli:
            try:
                return await self._generate_with_cli(prompt)
            except Exception as cli_error:
                # If CLI fails and we have API key, fallback to API
                if self.api_key and self.api_key != "dummy-key-for-cli":
                    error_str = str(cli_error)
                    print(f"⚠️  Gemini CLI failed: {error_str[:200]}")
                    print("🔄 Falling back to Gemini API for text generation...")
                    try:
                        return await self._generate_with_api(prompt)
                    except Exception as api_error:
                        # If API also fails, raise with both errors
                        raise Exception(f"Both CLI and API failed. CLI error: {error_str[:200]}. API error: {str(api_error)[:200]}")
                else:
                    # No API key, just raise CLI error
                    raise
        else:
            return await self._generate_with_api(prompt)
    
    async def generate_with_image(
        self, 
        prompt: str, 
        image_data: Union[str, bytes],
        mime_type: Optional[str] = None
    ) -> str:
        """
        Generate response with image input
        
        Args:
            prompt: Text prompt
            image_data: Base64 string or bytes of image
            mime_type: MIME type of image (auto-detected if not provided)
        
        Note: Images use API (better support), text-only uses CLI (better quotas)
        """
        # For images, ALWAYS use API directly (faster and more reliable)
        # CLI image support is slow and unreliable - NEVER use it
        if self.api_key and self.api_key != "dummy-key-for-cli":
            return await self._generate_with_image_api(prompt, image_data, mime_type)
        else:
            raise ValueError("GEMINI_API_KEY required for image processing. CLI image support is too slow and unreliable.")
    
    async def _generate_with_api(self, prompt: str) -> str:
        """Generate using direct API"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model_instance.generate_content(prompt)
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def _generate_with_cli(self, prompt: str) -> str:
        """Generate using Gemini CLI"""
        try:
            # Use headless mode with JSON output (longer timeout for large prompts like code generation)
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [
                        "gemini",
                        "-p", prompt,
                        "--output-format", "json",
                        "-m", self.model
                    ],
                    capture_output=True,
                    text=True,
                    timeout=180  # Increased timeout for large prompts (code generation can be 35k+ chars)
                )
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                
                # Try to read the error report file if mentioned
                if "Full report available at:" in error_msg:
                    try:
                        import re
                        match = re.search(r'Full report available at: (.+)', error_msg)
                        if match:
                            error_report_path = match.group(1).strip()
                            if os.path.exists(error_report_path):
                                with open(error_report_path, 'r') as f:
                                    error_report = json.load(f)
                                    error_details = error_report.get("error", {})
                                    detailed_msg = error_details.get("message", str(error_details))
                                    if detailed_msg and detailed_msg != "[object Object]":
                                        error_msg = f"{error_msg}\nDetailed error: {detailed_msg}"
                    except Exception as read_error:
                        pass  # If we can't read the report, use the original error
                
                raise Exception(f"Gemini CLI error: {error_msg}")
            
            # Parse JSON response
            try:
                response_data = json.loads(result.stdout)
                # Extract text from response
                if isinstance(response_data, dict):
                    return response_data.get("response", response_data.get("text", result.stdout))
                return result.stdout
            except json.JSONDecodeError:
                # If not JSON, return raw output
                return result.stdout
                
        except subprocess.TimeoutExpired:
            raise Exception("Gemini CLI request timed out after 180 seconds. The prompt might be too long. This will trigger API fallback.")
        except Exception as e:
            error_str = str(e)
            # Check if it's a known CLI error that should trigger API fallback
            if "Error when talking to Gemini API" in error_str or "cached credentials" in error_str.lower():
                raise Exception(f"Gemini CLI authentication/API error: {error_str[:500]}. This will trigger API fallback.")
            raise Exception(f"Gemini CLI error: {error_str[:500]}")
    
    async def _generate_with_image_api(
        self, 
        prompt: str, 
        image_data: Union[str, bytes],
        mime_type: Optional[str] = None
    ) -> str:
        """Generate with image using direct API"""
        try:
            # Convert base64 string to bytes if needed
            if isinstance(image_data, str):
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            # Auto-detect MIME type if not provided
            if not mime_type:
                from PIL import Image
                from io import BytesIO
                try:
                    with Image.open(BytesIO(image_bytes)) as img:
                        fmt = (img.format or "PNG").upper()
                        mime_type = f"image/{fmt.lower()}" if fmt != "JPEG" else "image/jpeg"
                except:
                    mime_type = "image/png"
            
            content = [
                prompt,
                {
                    "mime_type": mime_type,
                    "data": image_bytes
                }
            ]
            
            # Use longer timeout for image processing (complex UI images can take time)
            # Try with retries for better reliability
            max_retries = 2
            response = None
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    response = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: self.model_instance.generate_content(content)
                        ),
                        timeout=180.0  # Increased to 180 seconds for complex UI images
                    )
                    # Success - break out of retry loop
                    break
                except asyncio.TimeoutError as timeout_err:
                    last_error = timeout_err
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5  # Wait 5, 10 seconds between retries
                        print(f"⚠️  Image processing timeout (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        # Last attempt failed
                        raise
                except Exception as e:
                    # For non-timeout errors, don't retry
                    raise
            
            # Ensure we have a response
            if response is None:
                if last_error:
                    raise last_error
                else:
                    raise Exception("Failed to get response from Gemini API after retries")
            
            # Try to access text first - catch ValueError for safety blocks
            try:
                return response.text
            except ValueError as ve:
                error_msg = str(ve)
                # Check if it's the finish_reason error (no valid Part)
                if "finish_reason" in error_msg.lower() or "no valid Part" in error_msg or "Part" in error_msg:
                    # Get finish_reason from candidates
                    if response.candidates:
                        candidate = response.candidates[0]
                        finish_reason = candidate.finish_reason
                        finish_reason_str = str(finish_reason)
                        
                        # finish_reason 1 = SAFETY (content blocked) in Gemini API
                        # Check both int value and string representation
                        if finish_reason == 1 or "SAFETY" in finish_reason_str.upper():
                            safety_ratings = candidate.safety_ratings if hasattr(candidate, 'safety_ratings') else []
                            blocked_categories = []
                            if safety_ratings:
                                for rating in safety_ratings:
                                    prob = getattr(rating, 'probability', None)
                                    blocked = getattr(rating, 'blocked', False)
                                    if (prob and prob > 0.5) or blocked:
                                        category = getattr(rating, 'category', 'Unknown')
                                        blocked_categories.append(str(category))
                            
                            error_msg = "Content was blocked by Gemini safety filters"
                            if blocked_categories:
                                error_msg += f". Blocked categories: {', '.join(blocked_categories)}"
                            error_msg += ". This might be due to the image content or prompt. Please try a different image or modify the prompt."
                            raise Exception(error_msg)
                        elif finish_reason == 2 or "RECITATION" in finish_reason_str.upper():
                            raise Exception("Content was blocked due to potential recitation of copyrighted material. Please try a different image or prompt.")
                        elif finish_reason == 3 or "OTHER" in finish_reason_str.upper():
                            raise Exception("Content generation was stopped for an unknown reason. Please try again.")
                        elif finish_reason == 4 or "MAX_TOKENS" in finish_reason_str.upper():
                            raise Exception("Response was truncated due to token limit. The image might be too complex. Please try a simpler image.")
                        else:
                            raise Exception(f"Gemini API returned an invalid response. Finish reason: {finish_reason_str}. Please try again with a different image or prompt.")
                    else:
                        raise Exception("Gemini API returned an empty response. Please try again with a different image or prompt.")
                else:
                    # Re-raise if it's a different ValueError
                    raise
            
        except asyncio.TimeoutError:
            raise Exception("Gemini API request timed out after 180 seconds (with retries). The image might be too complex or the API is experiencing high load. Please try again or use a smaller/simpler image.")
        except Exception as e:
            error_str = str(e)
            # Don't fallback to CLI - just raise the error immediately
            if "429" in error_str or "quota" in error_str.lower():
                raise Exception(f"API quota exhausted (20 requests/day limit). Please wait 24 hours or use a different Google account with a new API key.")
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def _generate_with_image_cli(
        self, 
        prompt: str, 
        image_data: Union[str, bytes],
        mime_type: Optional[str] = None
    ) -> str:
        """
        Generate with image using Gemini CLI
        
        NOTE: CLI image processing is DISABLED - too slow and unreliable.
        This method should never be called for images.
        """
        # CLI image processing is completely disabled - always fail
        raise ValueError("CLI image processing is disabled. Use API with GEMINI_API_KEY for image processing.")
        try:
            # Convert base64 string to bytes if needed
            if isinstance(image_data, str):
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            # Auto-detect MIME type and extension
            from PIL import Image
            from io import BytesIO
            
            if not mime_type:
                try:
                    with Image.open(BytesIO(image_bytes)) as img:
                        fmt = (img.format or "PNG").upper()
                        ext = "png" if fmt == "PNG" else ("jpg" if fmt in ("JPG", "JPEG") else "png")
                        mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
                except:
                    ext = "png"
                    mime_type = "image/png"
            else:
                ext = mime_type.split("/")[-1].replace("jpeg", "jpg")
            
            # Create temporary file for image
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                tmp_file.write(image_bytes)
                tmp_path = tmp_file.name
            
            try:
                # Try using include-directories to reference the image
                # CLI can process images in the working directory
                image_dir = os.path.dirname(tmp_path)
                image_filename = os.path.basename(tmp_path)
                
                # Enhanced prompt that references the image file
                enhanced_prompt = f"""{prompt}

[Note: An image file named '{image_filename}' is available in the current directory. Please analyze this image as part of your response.]"""
                
                # Run CLI from the directory containing the image
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: subprocess.run(
                        [
                            "gemini",
                            "-p", enhanced_prompt,
                            "--include-directories", image_dir,
                            "--output-format", "json",
                            "-m", self.model
                        ],
                        capture_output=True,
                        text=True,
                        timeout=120,
                        cwd=image_dir  # Run from image directory
                    )
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout
                    print(f"⚠️  CLI image processing failed (exit code {result.returncode})")
                    print(f"   Error output: {error_msg[:500]}")
                    # If CLI fails with images, fall back to API if available
                    if self.api_key:
                        print("⚠️  Falling back to API for image processing")
                        return await self._generate_with_image_api(prompt, image_data, mime_type)
                    else:
                        raise Exception(f"Gemini CLI error: {error_msg}")
                
                # Parse JSON response
                try:
                    response_data = json.loads(result.stdout)
                    if isinstance(response_data, dict):
                        return response_data.get("response", response_data.get("text", result.stdout))
                    return result.stdout
                except json.JSONDecodeError:
                    return result.stdout
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            raise Exception("Gemini CLI request timed out")
        except Exception as e:
            # If CLI fails and we have API key, fall back
            if self.api_key and "CLI" in str(e):
                print("⚠️  CLI error, falling back to API")
                return await self._generate_with_image_api(prompt, image_data, mime_type)
            raise Exception(f"Gemini CLI error: {str(e)}")

