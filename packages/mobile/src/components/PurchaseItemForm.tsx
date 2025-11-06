import React from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { Controller, Control } from 'react-hook-form';
import type { ExpenseTypeRow } from '@agriplatform/shared';

interface PurchaseItemFormProps {
  index: number;
  control: Control<any>;
  expenseTypes: ExpenseTypeRow[];
  onRemove: () => void;
  showRemove: boolean;
}

export function PurchaseItemForm({
  index,
  control,
  expenseTypes,
  onRemove,
  showRemove,
}: PurchaseItemFormProps) {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Item {index + 1}</Text>
        {showRemove && (
          <TouchableOpacity onPress={onRemove} style={styles.deleteButton}>
            <Text style={styles.deleteText}>Delete</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Spending Type */}
      <View style={styles.field}>
        <Text style={styles.label}>Spending Type</Text>
        <Controller
          control={control}
          name={`items.${index}.expense_type_id`}
          rules={{ required: 'Spending type is required' }}
          render={({ field: { onChange, value }, fieldState: { error } }) => (
            <>
              <View style={styles.pickerContainer}>
                <Text style={styles.pickerText}>
                  {expenseTypes.find(t => t.id === value)?.name || 'Select type...'}
                </Text>
              </View>
              {error && <Text style={styles.errorText}>{error.message}</Text>}
            </>
          )}
        />
      </View>

      {/* Amount */}
      <View style={styles.field}>
        <Text style={styles.label}>Amount ($)</Text>
        <Controller
          control={control}
          name={`items.${index}.amount`}
          rules={{
            required: 'Amount is required',
            min: { value: 0.01, message: 'Amount must be greater than 0' },
          }}
          render={({ field: { onChange, onBlur, value }, fieldState: { error } }) => (
            <>
              <TextInput
                style={[styles.input, error && styles.inputError]}
                placeholder="0.00"
                keyboardType="decimal-pad"
                onBlur={onBlur}
                onChangeText={(text) => {
                  const numValue = parseFloat(text) || 0;
                  onChange(numValue);
                }}
                value={value ? value.toString() : ''}
              />
              {error && <Text style={styles.errorText}>{error.message}</Text>}
            </>
          )}
        />
      </View>

      {/* Description (for "Other" category) */}
      <Controller
        control={control}
        name={`items.${index}.other_category`}
        render={({ field: { onChange, onBlur, value } }) => (
          <View style={styles.field}>
            <Text style={styles.label}>Description (optional)</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter description"
              onBlur={onBlur}
              onChangeText={onChange}
              value={value || ''}
              multiline
            />
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#F5F5F5',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  deleteButton: {
    padding: 4,
  },
  deleteText: {
    color: '#C62828',
    fontSize: 14,
    fontWeight: '500',
  },
  field: {
    marginBottom: 12,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 6,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  inputError: {
    borderColor: '#C62828',
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#fff',
  },
  pickerText: {
    fontSize: 16,
    color: '#333',
  },
  errorText: {
    color: '#C62828',
    fontSize: 12,
    marginTop: 4,
  },
});
