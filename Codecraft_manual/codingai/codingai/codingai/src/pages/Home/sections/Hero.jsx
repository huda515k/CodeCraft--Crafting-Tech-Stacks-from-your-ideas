import React from "react";
import { Link } from "react-router-dom";

export default function Hero() {
  return (
    <section className="relative bg-linear-to-b from-blue-50 via-white to-gray-50 overflow-hidden">
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-blue-200 opacity-20 blur-3xl rounded-full"></div>
        <div className="absolute bottom-0 right-1/2 translate-x-1/2 w-[500px] h-[500px] bg-indigo-200 opacity-20 blur-3xl rounded-full"></div>
      </div>

      <div className="container mx-auto px-6 py-28 text-center flex flex-col items-center space-y-6">
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-gray-800 leading-tight max-w-5xl">
          Code <span className="text-blue-600">faster</span> with <br /> AI
          CodeCrafter
        </h1>

        <p className="text-gray-600 text-lg md:text-xl max-w-2xl leading-relaxed">
          CodeAssist AI Bot helps you debug, generate, and refine code in
          seconds. Stop wrestling with problems and start shipping smarter.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mt-6">
          <Link to="/chat">
            <button className="bg-blue-600 hover:bg-blue-700 text-white text-lg font-semibold py-3 px-10 hover:cursor-pointer rounded-full shadow-lg transition-all duration-300 hover:scale-105">
              Start Now
            </button>
          </Link>

          <button className="border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white hover:cursor-pointer text-lg font-semibold py-3 px-10 rounded-full transition-all duration-300">
            Learn More
          </button>
        </div>
      </div>
    </section>
  );
}
