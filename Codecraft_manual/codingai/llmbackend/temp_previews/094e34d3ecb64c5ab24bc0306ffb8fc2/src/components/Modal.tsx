import React from 'react';
import { Transition } from '@headlessui/react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => (
  <Transition appear show={isOpen} as={React.Fragment}>
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <Transition.Child
        as={React.Fragment}
        enter="ease-out duration-300"
        enterFrom="opacity-0 scale-95"
        enterTo="opacity-100 scale-100"
        leave="ease-in duration-200"
        leaveFrom="opacity-100 scale-100"
        leaveTo="opacity-0 scale-95"
      >
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
          {children}
          <button onClick={onClose} className="mt-4 text-red-500 hover:text-red-700">
            Close
          </button>
        </div>
      </Transition.Child>
    </div>
  </Transition>
);

export default Modal;