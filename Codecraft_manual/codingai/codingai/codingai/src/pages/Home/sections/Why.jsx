import React from "react";
import { IoMdClock, IoMdArrowDropright } from "react-icons/io";
import { FaArrowRightLong } from "react-icons/fa6";
import img from "../../../assets/banner2.jpg";

export default function Why() {
  const features = [
    {
      icon: <IoMdClock size={30} className="text-blue-600" />,
      title: "Save time",
      desc: "Cut hours of debugging and research down to minutes of conversation.",
    },
    {
      icon: <FaArrowRightLong size={30} className="text-purple-600" />,
      title: "Ship faster",
      desc: "Move from concept to production without getting stuck on implementation details.",
    },
    {
      icon: <IoMdArrowDropright size={30} className="text-pink-600" />,
      title: "Write better",
      desc: "Learn patterns and best practices while the AI refines your approach.",
    },
  ];

  return (
    <section className="bg-linear-to-b from-white via-gray-50 to-white py-20 px-5">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-12">
        <div className="md:w-1/2 overflow-hidden rounded-3xl shadow-lg hover:shadow-2xl transition-shadow duration-500">
          <img
            src={img}
            alt="Why CodeAssist"
            className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
          />
        </div>
        <div className="md:w-1/2 flex flex-col gap-8">
          <h2 className="text-3xl md:text-4xl font-extrabold text-gray-800 leading-tight">
            Why Developers Choose <span className="text-blue-600">code crafter AI</span>
          </h2>
          <p className="text-gray-600 text-lg">
            CodeAssist is built to make your workflow smoother, faster, and smarter.
            Here’s why it’s the go-to AI companion for modern developers:
          </p>
          <div className="flex flex-col gap-6">
            {features.map((item, i) => (
              <div
                key={i}
                className="flex items-start gap-5 bg-white p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1"
              >
                <div className="shrink-0 p-3 bg-gray-100 rounded-xl">
                  {item.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-xl text-gray-800">{item.title}</h3>
                  <p className="text-gray-600 mt-1 leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
