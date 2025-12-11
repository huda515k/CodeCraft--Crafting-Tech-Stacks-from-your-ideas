import React from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children?: React.ReactNode;
}

const Modal = ({ isOpen, onClose, children }: ModalProps) => (
  <div className={`fixed inset-0 flex items-center justify-center z-50 ${isOpen ? 'block' : 'hidden'}`}>
    <div className="bg-white p-4 rounded shadow-lg w-full max-w-md mx-auto">
      <button onClick={onClose} className="absolute top-2 right-2 bg-gray-100 hover:bg-gray-200 text-gray-500 focus:outline-none">
        &times;
      </button>
      {children}
    </div>
  </div>
);

export default Modal;