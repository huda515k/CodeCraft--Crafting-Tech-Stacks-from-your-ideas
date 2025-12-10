import React from "react";
import { FaGithub, FaTwitter, FaLinkedin } from "react-icons/fa";

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 py-10">
      <div className="container mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="text-center md:text-left">
          <h2 className="text-xl font-bold text-white">code crafter</h2>
          <p className="text-gray-400 text-sm">
            Your AI-powered coding companion. Build smarter, code faster.
          </p>
        </div>
        <div className="text-center md:text-right text-gray-400 text-sm">
          © 2025 <span className="text-white font-semibold">code crafter AI Bot</span>. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
