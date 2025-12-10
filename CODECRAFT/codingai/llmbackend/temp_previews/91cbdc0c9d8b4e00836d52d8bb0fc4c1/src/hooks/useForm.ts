import { useState, ChangeEvent, FormEvent } from 'react';

type FormValues = {
  [key: string]: any;
};

type FormErrors = {
  [key: string]: string;
};

type Validator<T> = (values: T) => FormErrors;

const useForm = <T extends FormValues>(initialValues: T, validate: Validator<T>) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setValues({
      ...values,
      [name]: value,
    });
    // Clear error for the field being changed
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = (callback: () => void) => (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    const validationErrors = validate(values);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length === 0) {
      callback();
    }
    setIsSubmitting(false);
  };

  const resetForm = (newValues: T = initialValues) => {
    setValues(newValues);
    setErrors({});
  };

  return {
    values,
    setValues,
    errors,
    handleChange,
    handleSubmit,
    isSubmitting,
    resetForm,
  };
};

export default useForm;