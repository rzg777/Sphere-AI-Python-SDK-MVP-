import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { showError } from '@/utils/toast';

interface UseValidationOptions<T extends z.ZodType> {
  schema: T;
  defaultValues?: Partial<z.infer<T>>;
  onSuccess?: (data: z.infer<T>) => void;
  onError?: (errors: any) => void;
}

export const useValidation = <T extends z.ZodType>({
  schema,
  defaultValues,
  onSuccess,
  onError,
}: UseValidationOptions<T>) => {
  const form = useForm<z.infer<T>>({
    resolver: zodResolver(schema),
    defaultValues: defaultValues as any,
    mode: 'onChange',
  });

  const handleSubmit = form.handleSubmit(async (data) => {
    try {
      // Validate with Zod schema
      const validatedData = await schema.parseAsync(data);
      
      if (onSuccess) {
        await onSuccess(validatedData);
      }
    } catch (error) {
      if (error instanceof z.ZodError) {
        const firstError = error.errors[0];
        showError(firstError?.message || 'Validation failed');
      } else {
        showError('An unexpected error occurred');
      }
      
      if (onError) {
        onError(error);
      }
    }
  });

  return {
    ...form,
    handleSubmit,
    isValid: form.formState.isValid,
    isSubmitting: form.formState.isSubmitting,
    errors: form.formState.errors,
  };
};

// Pre-configured validation hooks for common forms
export const useLoginValidation = (onSuccess?: (data: any) => void) => {
  const { loginSchema } = await import('@/lib/validation');
  return useValidation({
    schema: loginSchema,
    onSuccess,
  });
};

export const useProfileValidation = (defaultValues?: any, onSuccess?: (data: any) => void) => {
  const { profileSchema } = await import('@/lib/validation');
  return useValidation({
    schema: profileSchema,
    defaultValues,
    onSuccess,
  });
};

export const useTextInputValidation = (onSuccess?: (data: any) => void) => {
  const { textInputSchema } = await import('@/lib/validation');
  return useValidation({
    schema: textInputSchema,
    onSuccess,
  });
};