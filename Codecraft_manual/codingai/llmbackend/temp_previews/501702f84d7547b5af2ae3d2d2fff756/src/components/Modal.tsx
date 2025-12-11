import React from 'react';

interface ModalProps {
  children?: React.ReactNode;
  onClose: () => void;
}

const Modal: React.FC<ModalProps> = ({ children, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-4 rounded shadow-lg w-full max-w-md">
        {children}
        <button
          onClick={onClose}
          className="mt-4 bg-gray-200 px-3 py-2 rounded hover:bg-gray-300"
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default Modal;