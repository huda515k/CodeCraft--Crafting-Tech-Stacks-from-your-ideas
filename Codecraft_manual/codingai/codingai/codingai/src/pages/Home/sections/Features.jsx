import React from "react";
import { BsBug } from "react-icons/bs";
import { SiJsfiddle } from "react-icons/si";
import { RiCodeFill } from "react-icons/ri";

export default function Features() {
  const features = [
    {
      icon: <RiCodeFill size={50} className="text-blue-600" />,
      title: "Code generation",
      desc: "Generate working code from plain language descriptions in seconds.",
      gradient: "from-blue-50 to-white",
    },
    {
      icon: <BsBug size={50} className="text-purple-600" />,
      title: "Debugging assistance",
      desc: "Identify bugs and get fixes without endless searches through documentation.",
      gradient: "from-purple-50 to-white",
    },
    {
      icon: <SiJsfiddle size={50} className="text-pink-600" />,
      title: "Multi-language support",
      desc: "Work in Python, JavaScript, Java, C++, Go, and more with equal ease.",
      gradient: "from-pink-50 to-white",
    },
  ];

  return (
    <section id="features" className="bg-linear-to-b from-white via-gray-50 to-white py-20 px-6">
      <div className="max-w-7xl mx-auto text-center space-y-12">
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-blue-600 uppercase tracking-wider">
            Features
          </h2>
          <h1 className="text-3xl md:text-5xl lg:text-6xl font-extrabold text-gray-800 leading-tight">
            What code crafter AI Bot Does for You
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto text-lg">
            Three core capabilities built to handle the work that slows you down. Write better code, faster.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-10 mt-10">
          {features.map((item, i) => (
            <div
              key={i}
              className={`p-8 rounded-3xl bg-linear-to-b ${item.gradient} shadow-md hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border border-gray-100 flex flex-col items-center text-center`}
            >
              <div className="p-4 bg-white shadow-md rounded-2xl mb-5">
                {item.icon}
              </div>
              <h3 className="font-bold text-2xl text-gray-800 mb-3">
                {item.title}
              </h3>
              <p className="text-gray-600 text-base">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
