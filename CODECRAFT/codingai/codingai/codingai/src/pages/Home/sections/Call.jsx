import React from "react";

export default function Call() {
  return (
    <section className="relative bg-linear-to-r from-blue-50 via-white to-blue-100 py-20 px-6 overflow-hidden">
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-200 opacity-30 blur-3xl rounded-full"></div>
      </div>
      <div className="container mx-auto text-center flex flex-col items-center space-y-5">
        <h1 className="text-3xl md:text-5xl font-extrabold text-gray-800 leading-tight">
          Ready to <span className="text-blue-600">code smarter?</span>
        </h1>
        <p className="text-gray-600 text-lg md:text-xl max-w-2xl">
          Stop wasting time on problems you've solved before — start using
          <span className="text-blue-600 font-semibold"> code crafter AI </span>
          and get instant help right inside your workflow.
        </p>

        <button className="mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-lg py-3 px-10 rounded-full shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105 hover:cursor-pointer">
          Try Chatbot
        </button>
      </div>
    </section>
  );
}
