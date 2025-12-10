import React, { useState } from "react";
import { FiMenu, FiX } from "react-icons/fi";
import { Link } from "react-router-dom";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);
  const closeMenu = () => setIsOpen(false);

  return (
    <header className="bg-white shadow-sm fixed top-0 left-0 w-full z-50">
      <div className="container mx-auto flex justify-between items-center py-4 px-6">
        <h1 className="text-2xl md:text-3xl font-extrabold text-blue-600 tracking-tight cursor-pointer">
          CodeCrafter<span className="text-gray-800">AI</span>
        </h1>
        <nav className="hidden md:flex gap-8 text-gray-700 font-medium">
          <a
            href="#features"
            className="hover:text-blue-600 transition-all duration-300"
          >
            Features
          </a>
          <a
            href="#faq"
            className="hover:text-blue-600 transition-all duration-300"
          >
            FAQ
          </a>
        </nav>
        <Link to="/chat">
          <button className="hidden md:block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-full shadow-md hover:cursor-pointer hover:shadow-lg transition-all duration-300">
            Try Now
          </button>
        </Link>
        <div className="md:hidden">
          <button
            onClick={toggleMenu}
            className="text-2xl text-gray-700 hover:text-blue-600 transition-all"
            aria-label="Toggle menu"
          >
            {isOpen ? <FiX /> : <FiMenu />}
          </button>
        </div>
      </div>
      {isOpen && (
        <div className="md:hidden bg-white border-t border-gray-200 shadow-md transition-all duration-300">
          <nav className="flex flex-col items-center py-4 space-y-4 text-gray-700 font-medium">
            <a
              href="#features"
              onClick={closeMenu}
              className="hover:text-blue-600 transition-all"
            >
              Features
            </a>
            <a
              href="#faq"
              onClick={closeMenu}
              className="hover:text-blue-600 transition-all"
            >
              FAQ
            </a>
            <a
              href="#contact"
              onClick={closeMenu}
              className="hover:text-blue-600 transition-all"
            >
              Contact
            </a>
            <button
              onClick={closeMenu}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-full shadow-md transition-all duration-300"
            >
              Try Now
            </button>
          </nav>
        </div>
      )}
    </header>
  );
}
