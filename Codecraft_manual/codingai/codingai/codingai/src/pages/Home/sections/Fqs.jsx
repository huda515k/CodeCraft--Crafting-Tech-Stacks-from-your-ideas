import React, { useState } from "react";
import { ChevronDown } from "lucide-react";

export default function Fqs() {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: "Is my code secure?",
      answer:
        "Your code stays private. We don't store snippets or use them for training. Encryption protects everything in transit and at rest.",
    },
    {
      question: "What languages are supported?",
      answer:
        "CodeAssist handles Python, JavaScript, Java, C++, Go, Rust, TypeScript, and more. The AI understands syntax and idioms across all major languages.",
    },
    {
      question: "How fast are the responses?",
      answer:
        "Most answers come back in under two seconds. Complex debugging tasks might take a few seconds longer, but you're never waiting around.",
    },
    {
      question: "Can I use this offline?",
      answer:
        "CodeAssist requires an internet connection to function. The AI runs on our servers, so you need to stay connected to get assistance.",
    },
  ];

  const toggleFaq = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="bg-linear-to-b from-gray-50 to-white py-20 px-5">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-800 mb-4">
            Frequently Asked Questions
          </h1>
          <p className="text-gray-600 text-lg">
            Everything you need to know about{" "}
            <span className="text-blue-600 font-semibold">code crafter AI Bot</span> and how it works.
          </p>
        </div>
        <div className="flex flex-col gap-6">
          {faqs.map((faq, i) => (
            <div
              key={i}
              onClick={() => toggleFaq(i)}
              className="p-6 rounded-2xl shadow-md hover:shadow-lg transition-all duration-300 bg-white border border-gray-100 cursor-pointer"
            >
              <div className="flex justify-between items-center">
                <h2 className="text-xl md:text-2xl font-semibold text-gray-800">
                  {faq.question}
                </h2>
                <ChevronDown
                  className={`w-6 h-6 text-blue-500 transition-transform duration-300 ${
                    openIndex === i ? "rotate-180" : "rotate-0"
                  }`}
                />
              </div>
              <div
                className={`mt-3 text-gray-600 leading-relaxed transition-all duration-300 ${
                  openIndex === i
                    ? "max-h-40 opacity-100"
                    : "max-h-0 opacity-0 overflow-hidden"
                }`}
              >
                {faq.answer}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
