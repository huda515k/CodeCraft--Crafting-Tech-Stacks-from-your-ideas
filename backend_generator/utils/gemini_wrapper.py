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
            # Try both 'gemini' and 'gemini-cli' commands
            for cmd in ["gemini", "gemini-cli"]:
                try:
                    result = subprocess.run(
                        [cmd, "--version"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"✅ Found Gemini CLI: {cmd}")
                        return True
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            return False
        except Exception:
            return False
    
    def _map_model_for_api(self, model: str) -> str:
        """Map CLI model names to API model names"""
        # Map to actual Gemini API model names that are available
        # Try to use the model name directly if it's available in API
        # gemini-2.5-flash is available in API, so use it directly
        model_mapping = {
            "gemini-2.5-pro": "gemini-2.5-pro",  # Try direct first
            "gemini-2.5-flash": "gemini-2.5-flash",  # Available in API - use directly
            "gemini-2.5-flash-lite": "gemini-2.5-flash",  # Fallback to flash
            "gemini-3-pro-preview": "gemini-2.5-pro",  # Try 2.5-pro
            "gemini-flash-latest": "gemini-2.5-flash",  # Use 2.5-flash directly
            "gemini-1.5-flash": "gemini-2.5-flash",  # Upgrade to 2.5
            "gemini-1.5-flash-latest": "gemini-2.5-flash",  # Upgrade to 2.5
        }
        # Default to gemini-2.5-flash which is available in API
        return model_mapping.get(model, "gemini-2.5-flash")
    
    def _map_model_for_cli(self, model: str, for_image: bool = False) -> str:
        """Map model names to CLI-compatible model names"""
        # CLI model name mapping - CLI might use different names than API
        # For image processing, use vision-capable models
        if for_image:
            # Vision-capable models for CLI
            # Note: gemini-1.5-flash was deprecated Sep 29, 2025. Use gemini-2.5-flash instead
            vision_model_mapping = {
                "gemini-flash-latest": "gemini-2.5-flash",  # Use 2.5-flash (deprecated 1.5-flash)
                "gemini-2.5-flash": "gemini-2.5-flash",  # Use directly
                "gemini-2.5-pro": "gemini-2.5-pro",  # Use directly
                "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",  # Use directly
                "gemini-3-pro-preview": "gemini-2.5-pro",  # Fallback to 2.5-pro
            }
            return vision_model_mapping.get(model, "gemini-2.5-flash")  # Default to 2.5-flash
        
        # Text-only models - use current available models (2.5 series)
        # Note: gemini-1.5-flash was deprecated. Use gemini-2.5-flash instead
        cli_model_mapping = {
            "gemini-flash-latest": "gemini-2.5-flash",  # Use 2.5-flash
            "gemini-2.5-flash": "gemini-2.5-flash",  # Use directly
            "gemini-2.5-pro": "gemini-2.5-pro",  # Use directly
            "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",  # Use directly
            "gemini-3-pro-preview": "gemini-2.5-pro",  # Fallback to 2.5-pro
        }
        return cli_model_mapping.get(model, "gemini-2.5-flash")  # Default to 2.5-flash
    
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
        
        Note: Tries API first, falls back to CLI if API has quota/errors
        """
        # Try API first (faster and more reliable)
        if self.api_key and self.api_key != "dummy-key-for-cli":
            try:
                return await self._generate_with_image_api(prompt, image_data, mime_type)
            except Exception as api_error:
                error_str = str(api_error)
                # If API fails due to quota, model not found (404), or other errors, try CLI as fallback
                should_fallback = (
                    "API_QUOTA_ERROR" in error_str or 
                    "quota" in error_str.lower() or 
                    "429" in error_str or 
                    "exhausted" in error_str.lower() or
                    "404" in error_str or
                    "not found" in error_str.lower() or
                    "notFound" in error_str or
                    "models/" in error_str and "not found" in error_str.lower()
                )
                
                if should_fallback:
                    print(f"⚠️  API error detected: {error_str[:200]}")
                    if self.use_cli:
                        print("🔄 Falling back to Gemini CLI for image processing...")
                        print("⚠️  Note: CLI uses the same API backend, so if API quota is exhausted, CLI will also fail.")
                        try:
                            return await self._generate_with_image_cli(prompt, image_data, mime_type)
                        except Exception as cli_error:
                            cli_error_str = str(cli_error)
                            # Check if CLI also hit quota or API issues
                            if "quota" in cli_error_str.lower() or "exhausted" in cli_error_str.lower() or "error when talking to gemini api" in cli_error_str.lower():
                                raise Exception(f"Both API and CLI failed for image processing due to exhausted Gemini API quota. The CLI uses the same API backend, so when API quota is exhausted, CLI will also fail. Please wait for quota reset (usually 24 hours) or use a different Google account with available quota. API error: {error_str[:200]}. CLI error: {cli_error_str[:200]}")
                            elif "unable to directly analyze" in cli_error_str.lower() or "local file path" in cli_error_str.lower() or "not a test file" in cli_error_str.lower():
                                # CLI cannot process local image files - this is a CLI limitation
                                raise Exception(f"CLI cannot process local image files directly. The Gemini CLI has limitations with local file paths and cannot analyze images from file system paths. Since the API quota is exhausted and CLI cannot process local images, image processing is currently unavailable. Solutions: 1) Wait for API quota reset (usually 24 hours), 2) Use a different Google account with available quota, 3) Upload image to a publicly accessible URL. CLI error: {cli_error_str[:400]}")
                            else:
                                raise Exception(f"Both API and CLI failed. API error: {error_str[:200]}. CLI error: {cli_error_str[:200]}")
                    else:
                        # No CLI available, raise with helpful message
                        raise Exception(f"API error and CLI not available. Please install Gemini CLI: npm install -g @google/generative-ai-cli && gemini auth login")
                else:
                    # For other errors, don't fallback - just raise
                    raise
        elif self.use_cli:
            # No API key, use CLI directly
            return await self._generate_with_image_cli(prompt, image_data, mime_type)
        else:
            raise ValueError("Either GEMINI_API_KEY or Gemini CLI (with OAuth) is required for image processing.")
    
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
            # Map model name for CLI compatibility
            cli_model = self._map_model_for_cli(self.model)
            
            # Set NODE_OPTIONS to suppress warnings
            env = os.environ.copy()
            env['NODE_OPTIONS'] = '--no-warnings'
            
            # Use headless mode with JSON output (longer timeout for large prompts like code generation)
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [
                        "gemini",
                        "-p", prompt,
                        "--output-format", "json",
                        "-m", cli_model
                    ],
                    capture_output=True,
                    text=True,
                    timeout=180,  # Increased timeout for large prompts (code generation can be 35k+ chars)
                    env=env  # Pass environment with NODE_OPTIONS
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
            # Check for quota errors - these should trigger CLI fallback
            if "429" in error_str or "quota" in error_str.lower() or "exhausted" in error_str.lower():
                # Raise a specific exception that can be caught for fallback
                raise Exception(f"API_QUOTA_ERROR: API quota exhausted. This will trigger CLI fallback if available.")
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def _generate_with_image_cli(
        self, 
        prompt: str, 
        image_data: Union[str, bytes],
        mime_type: Optional[str] = None
    ) -> str:
        """
        Generate with image using Gemini CLI
        
        NOTE: CLI image processing has limitations - it may not process local image files directly.
        Since API quota is exhausted, we'll try CLI but may need to use a workaround.
        """
        # CLI image processing - try to use the image file, but CLI has limitations
        try:
            # Convert base64 string to bytes if needed
            if isinstance(image_data, str):
                image_bytes = base64.b64decode(image_data)
                image_base64_str = image_data  # Keep original base64 string
            else:
                image_bytes = image_data
                image_base64_str = base64.b64encode(image_bytes).decode('utf-8')
            
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
            
            # Optimize image for CLI processing - reduce size more aggressively to prevent timeouts
            # CLI has issues with very large base64-embedded images, so we'll compress more
            original_size_bytes = len(image_bytes)
            try:
                from PIL import Image
                from io import BytesIO
                img = Image.open(BytesIO(image_bytes))
                original_size = img.size
                original_format = img.format or 'PNG'
                
                # For CLI, use smaller max dimension (1024px) to reduce base64 size and processing time
                max_dimension_cli = 1024
                if max(original_size) > max_dimension_cli:
                    print(f"📐 Optimizing image for CLI: resizing from {original_size} to max {max_dimension_cli}px...")
                    ratio = max_dimension_cli / max(original_size)
                    new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Convert to RGB if needed (for JPEG compression)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                        ext = "jpg"
                        mime_type = "image/jpeg"
                    
                    # Compress more aggressively for CLI (quality=75 for JPEG, optimize for PNG)
                    output = BytesIO()
                    if ext.lower() in ('jpg', 'jpeg'):
                        img.save(output, format='JPEG', quality=75, optimize=True)
                    else:
                        img.save(output, format='PNG', optimize=True)
                    image_bytes = output.getvalue()
                    print(f"✅ Image optimized for CLI: {img.size}, size: {len(image_bytes)} bytes (reduced from {original_size_bytes} bytes)")
            except Exception as opt_error:
                print(f"⚠️  Could not optimize image for CLI: {opt_error}, using original ({original_size_bytes} bytes)")
            
            # Create temporary file for image
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                tmp_file.write(image_bytes)
                tmp_path = tmp_file.name
            
            try:
                # Map model name for CLI compatibility - use vision-capable model for images
                cli_model = self._map_model_for_cli(self.model, for_image=True)
                print(f"🔧 Using CLI model for images: {cli_model} (mapped from {self.model})")
                
                # Try both 'gemini' and 'gemini-cli' commands
                cli_cmd = None
                for cmd in ["gemini", "gemini-cli"]:
                    try:
                        result_check = subprocess.run(
                            [cmd, "--version"],
                            capture_output=True,
                            timeout=2
                        )
                        if result_check.returncode == 0:
                            cli_cmd = cmd
                            break
                    except (FileNotFoundError, subprocess.TimeoutExpired):
                        continue
                
                if not cli_cmd:
                    raise Exception("Gemini CLI not found. Install with: npm install -g @google/generative-ai-cli")
                
                # Gemini CLI supports passing image files directly as arguments
                # For gemini-cli: gemini-cli prompt --model MODEL "prompt" image.jpg
                # For gemini: Use @ syntax: gemini -m MODEL "prompt @image.jpg" (or positional)
                # Set NODE_OPTIONS to suppress warnings that might cause CLI to exit with error code
                env = os.environ.copy()
                env['NODE_OPTIONS'] = '--no-warnings'
                
                if cli_cmd == "gemini-cli":
                    # Use gemini-cli syntax: gemini-cli prompt --model MODEL "prompt" image.jpg
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: subprocess.run(
                            [
                                "gemini-cli",
                                "prompt",
                                "--model", cli_model,
                                "--output-format", "json",
                                prompt,
                                tmp_path
                            ],
                            capture_output=True,
                            text=True,
                            timeout=300,  # Increased timeout for image processing (5 minutes)
                            env=env  # Pass environment with NODE_OPTIONS
                        )
                    )
                else:
                    # For 'gemini' CLI, try multiple approaches to pass the image
                    import base64 as b64
                    
                    # Approach 1: Try file path with @ syntax
                    print(f"🔍 Attempting CLI with file path (@ syntax): {tmp_path}")
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: subprocess.run(
                            [
                                "gemini",
                                "-m", cli_model,
                                f"{prompt} @{tmp_path}"
                            ],
                            capture_output=True,
                            text=True,
                            timeout=300,
                            env=env
                        )
                    )
                    
                    # Check if file path approach worked
                    file_path_worked = False
                    if result.returncode == 0:
                        # Check if stdout contains valid JSON (not an error message)
                        stdout_lower = (result.stdout or "").lower()
                        if result.stdout and len(result.stdout.strip()) > 50:
                            # Check if it's not an error message about not being able to process images
                            if "cannot" not in stdout_lower and "unable" not in stdout_lower and "sorry" not in stdout_lower:
                                if "{" in result.stdout or "response" in stdout_lower:
                                    print(f"✅ File path approach worked!")
                                    file_path_worked = True
                    
                    # Approach 2: If file path didn't work, try positional argument
                    if not file_path_worked:
                        print(f"⚠️  File path @ syntax failed (exit code: {result.returncode}), trying positional argument...")
                        print(f"   Error: {result.stderr[:200] if result.stderr else result.stdout[:200]}")
                        
                        result = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: subprocess.run(
                                [
                                    "gemini",
                                    "-m", cli_model,
                                    prompt,
                                    tmp_path  # Positional argument
                                ],
                                capture_output=True,
                                text=True,
                                timeout=300,
                                env=env
                            )
                        )
                        
                        # Check if positional argument worked
                        if result.returncode == 0:
                            stdout_lower = (result.stdout or "").lower()
                            if result.stdout and len(result.stdout.strip()) > 50:
                                if "cannot" not in stdout_lower and "unable" not in stdout_lower and "sorry" not in stdout_lower:
                                    if "{" in result.stdout or "response" in stdout_lower:
                                        print(f"✅ Positional argument approach worked!")
                                        file_path_worked = True
                    
                    # Approach 3: If both file path approaches failed, check if it's because CLI can't process images
                    if not file_path_worked:
                        error_output = (result.stderr or result.stdout or "").lower()
                        if "cannot" in error_output or "unable" in error_output or "sorry" in error_output or "base64" in error_output:
                            # CLI explicitly says it can't process images
                            raise Exception(f"Gemini CLI cannot process image files. The CLI returned: {result.stdout[:500] if result.stdout else result.stderr[:500]}. This is a CLI limitation. Please wait for API quota reset or use a different Google account with available quota.")
                        
                        # If we get here, the file path approaches failed but not due to image processing limitation
                        # Don't try base64 embedding - it won't work either
                        error_msg = result.stderr or result.stdout or "Unknown error"
                        raise Exception(f"Gemini CLI file path approaches failed. Exit code: {result.returncode}. Error: {error_msg[:500]}. Note: CLI cannot process base64-embedded images, so file path must work.")
                
                # Check for Node.js warnings in stderr that might cause non-zero exit code
                # Sometimes CLI returns valid output in stdout despite warnings in stderr
                # Also check for CLI's inability to process images
                error_output = (result.stderr or result.stdout or "").lower()
                cannot_process_images = (
                    "cannot" in error_output and ("process" in error_output or "see" in error_output or "image" in error_output) and "base64" in error_output
                ) or "unable to analyze" in error_output or "sorry" in error_output and "image" in error_output
                
                if cannot_process_images:
                    # CLI explicitly says it can't process images - don't try base64, just fail clearly
                    full_error = result.stdout or result.stderr or "Unknown error"
                    raise Exception(f"Gemini CLI cannot process image files. The CLI returned: {full_error[:500]}. This is a CLI limitation - the CLI cannot process images via file paths or base64. Since API quota is exhausted, image processing is currently unavailable. Solutions: 1) Wait for API quota reset (usually 24 hours), 2) Use a different Google account with available quota, 3) Check if API quota has reset: https://ai.dev/usage?tab=rate-limit")
                
                if result.returncode != 0:
                    # Check if stdout has valid content despite non-zero exit code
                    if result.stdout and len(result.stdout.strip()) > 50:
                        # Check if stdout looks like a valid response (JSON or text)
                        stdout_lower = result.stdout.lower()
                        if "{" in result.stdout or "response" in stdout_lower or ("error" not in stdout_lower[:200] and "cannot" not in stdout_lower[:200]):
                            print(f"⚠️  CLI exited with code {result.returncode}, but stdout has content. Using stdout as response...")
                            print(f"   Stdout length: {len(result.stdout)}")
                            print(f"   Stderr: {result.stderr[:200] if result.stderr else 'None'}")
                            # Treat as success if stdout has valid content
                            result.returncode = 0
                        else:
                            error_msg = result.stderr or result.stdout
                            print(f"⚠️  CLI image processing failed (exit code {result.returncode})")
                            print(f"   Error output: {error_msg[:500]}")
                            
                            # Check for Node.js warnings
                            if "unsettled top-level await" in error_msg or result.returncode == 13:
                                raise Exception(f"CLI failed due to Node.js ESM warning (exit code {result.returncode}). This is a known issue with the Gemini CLI. Try updating: npm update -g @google/generative-ai-cli. Error: {error_msg[:400]}")
                            
                            # Check for specific CLI limitations
                            if "unable to directly analyze" in error_msg.lower() or "local file path" in error_msg.lower():
                                raise Exception(f"CLI cannot process local image files. The Gemini CLI has limitations with local file paths and cannot analyze images from the file system. Since API quota is exhausted, image processing is unavailable. Please wait for API quota reset or use a different account. Error: {error_msg[:400]}")
                    else:
                        error_msg = result.stderr or result.stdout
                        print(f"⚠️  CLI image processing failed (exit code {result.returncode})")
                        print(f"   Error output: {error_msg[:500]}")
                        
                        # Check for Node.js warnings
                        if "unsettled top-level await" in error_msg or result.returncode == 13:
                            raise Exception(f"CLI failed due to Node.js ESM warning (exit code {result.returncode}). This is a known issue with the Gemini CLI. Try updating: npm update -g @google/generative-ai-cli. Error: {error_msg[:400]}")
                        
                        # Check for specific CLI limitations
                        if "unable to directly analyze" in error_msg.lower() or "local file path" in error_msg.lower():
                            raise Exception(f"CLI cannot process local image files. The Gemini CLI has limitations with local file paths and cannot analyze images from the file system. Since API quota is exhausted, image processing is unavailable. Please wait for API quota reset or use a different account. Error: {error_msg[:400]}")
                    
                    # Try to read the full error report if mentioned
                    detailed_error = error_msg
                    if "Full report available at:" in error_msg:
                        try:
                            import re
                            match = re.search(r'Full report available at: (.+)', error_msg)
                            if match:
                                error_report_path = match.group(1).strip()
                                print(f"📄 Error report path: {error_report_path}")
                                
                                # The path might be incomplete, try to find the actual file
                                if not os.path.exists(error_report_path):
                                    # Try to find files matching the pattern
                                    import glob
                                    # Try multiple base paths
                                    possible_bases = [
                                        error_report_path.rsplit('/', 1)[0] if '/' in error_report_path else None,
                                        '/var/folders',
                                        '/tmp',
                                        os.path.expanduser('~/.gemini/tmp')
                                    ]
                                    
                                    for base_path in possible_bases:
                                        if not base_path:
                                            continue
                                        pattern = os.path.join(base_path, '**/*error*.json')
                                        matches = glob.glob(pattern, recursive=True)
                                        if matches:
                                            # Get the most recent error report
                                            error_report_path = max(matches, key=os.path.getmtime)
                                            print(f"📄 Found error report: {error_report_path}")
                                            break
                                
                                if os.path.exists(error_report_path):
                                    with open(error_report_path, 'r') as f:
                                        error_report = json.load(f)
                                        error_details = error_report.get("error", {})
                                        detailed_msg = error_details.get("message", str(error_details))
                                        error_code = error_details.get("code", "")
                                        
                                        # Parse nested error if it's a string
                                        if isinstance(detailed_msg, str) and "error" in detailed_msg.lower():
                                            try:
                                                import json as json_module
                                                nested_error = json_module.loads(detailed_msg)
                                                if isinstance(nested_error, list) and len(nested_error) > 0:
                                                    nested_error_obj = nested_error[0].get("error", {})
                                                    detailed_msg = nested_error_obj.get("message", detailed_msg)
                                                    error_code = nested_error_obj.get("code", error_code)
                                            except:
                                                pass
                                        
                                        if detailed_msg and detailed_msg != "[object Object]":
                                            detailed_error = f"{error_msg}\nDetailed error: {detailed_msg}"
                                            if error_code:
                                                detailed_error += f"\nError code: {error_code}"
                        except Exception as read_error:
                            print(f"⚠️  Could not read error report: {read_error}")
                    
                    # Check for specific error types
                    if "Error when talking to Gemini API" in error_msg or "404" in detailed_error or "not found" in detailed_error.lower():
                        # This could be model not found or quota issue
                        if "404" in detailed_error or "not found" in detailed_error.lower():
                            raise Exception(f"Gemini CLI model not found (404): The model '{cli_model}' may not be available. Try using a different model. Full error: {detailed_error[:800]}")
                        else:
                            raise Exception(f"Gemini CLI API error: The CLI uses the same Gemini API. If API quota is exhausted, CLI will also fail. Please wait for quota reset. Full error: {detailed_error[:800]}")
                    
                    # If CLI fails, we can't fall back to API (API quota is exhausted)
                    # So we raise the error with helpful message
                    raise Exception(f"Gemini CLI image processing failed: {detailed_error[:800]}. Please check that Gemini CLI is properly installed and authenticated: npm install -g @google/generative-ai-cli && gemini auth login")
                
                # Parse response - CLI might return JSON or plain text
                print(f"📥 CLI stdout length: {len(result.stdout)}")
                print(f"📥 CLI stdout (first 300 chars): {result.stdout[:300]}")
                
                # Try to parse as JSON first
                try:
                    response_data = json.loads(result.stdout)
                    if isinstance(response_data, dict):
                        # Extract text from JSON response
                        # CLI returns: {"response": "actual text here", "stats": {...}}
                        text = response_data.get("response") or response_data.get("text") or response_data.get("content")
                        
                        if text:
                            print(f"✅ Extracted text from CLI JSON response, length: {len(text)}")
                            print(f"📝 Text preview (first 200 chars): {text[:200]}")
                            # Return the extracted text (which should be the JSON UI analysis)
                            return text if isinstance(text, str) else str(text)
                        else:
                            # No text field, return the whole dict as string
                            print(f"⚠️  No 'response' field in CLI JSON, returning full JSON")
                            return json.dumps(response_data)
                    else:
                        # Not a dict, return as string
                        return str(response_data)
                except json.JSONDecodeError:
                    # Not JSON, return as-is (might be plain text response)
                    print(f"⚠️  Response is not JSON, returning as plain text")
                    return result.stdout
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            raise Exception("Gemini CLI image processing timed out after 300 seconds. The image might be too complex or CLI is experiencing issues. Try: 1) Using a smaller/simpler image, 2) Waiting for API quota reset, 3) Checking CLI installation: npm update -g @google/generative-ai-cli")
        except Exception as e:
            # If we're here, it means we're using CLI as fallback (API quota exhausted)
            # So we can't fall back to API - just raise the error
            error_str = str(e)
            if "CLI image processing is disabled" not in error_str:  # Don't double-wrap the error
                raise Exception(f"Gemini CLI image processing error: {error_str[:500]}. Please ensure Gemini CLI is installed and authenticated: npm install -g @google/generative-ai-cli && gemini-cli auth login")
            raise

