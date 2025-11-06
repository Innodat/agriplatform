import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Modal,
  ScrollView,
} from 'react-native';
import { Controller, Control } from 'react-hook-form';
import type { ExpenseTypeRow } from '@agriplatform/shared';

interface PurchaseItemFormProps {
  index: number;
  control: Control<any>;
  expenseTypes: ExpenseTypeRow[];
  onRemove: () => void;
  showRemove: boolean;
  currencySymbol: string;
}

export function PurchaseItemForm({
  index,
  control,
  expenseTypes,
  onRemove,
  showRemove,
  currencySymbol,
}: PurchaseItemFormProps) {
  const [showExpenseTypePicker, setShowExpenseTypePicker] = useState(false);

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
        <Text style={styles.label}>Spending Type *</Text>
        <Controller
          control={control}
          name={`items.${index}.expense_type_id`}
          rules={{ required: 'Spending type is required' }}
          render={({ field: { onChange, value }, fieldState: { error } }) => {
            const selectedType = expenseTypes.find(t => t.id === value);
            return (
              <>
                <TouchableOpacity
                  style={[styles.pickerContainer, error && styles.pickerError]}
                  onPress={() => setShowExpenseTypePicker(true)}
                >
                  <Text style={[styles.pickerText, !selectedType && styles.placeholderText]}>
                    {selectedType?.name || 'Select type...'}
                  </Text>
                </TouchableOpacity>
                {error && <Text style={styles.errorText}>{error.message}</Text>}

                {/* Expense Type Picker Modal */}
                <Modal
                  visible={showExpenseTypePicker}
                  transparent
                  animationType="slide"
                  onRequestClose={() => setShowExpenseTypePicker(false)}
                >
                  <TouchableOpacity 
                    style={styles.modalOverlay}
                    activeOpacity={1}
                    onPress={() => setShowExpenseTypePicker(false)}
                  >
                    <TouchableOpacity 
                      style={styles.modalContent}
                      activeOpacity={1}
                      onPress={(e) => e.stopPropagation()}
                    >
                      <View style={styles.modalHeader}>
                        <Text style={styles.modalTitle}>Select Spending Type</Text>
                        <TouchableOpacity onPress={() => setShowExpenseTypePicker(false)}>
                          <Text style={styles.modalClose}>✕</Text>
                        </TouchableOpacity>
                      </View>
                      <ScrollView style={styles.modalScrollView}>
                        {expenseTypes.map((type) => (
                          <TouchableOpacity
                            key={type.id}
                            style={styles.modalItem}
                            onPress={() => {
                              onChange(type.id);
                              setShowExpenseTypePicker(false);
                            }}
                          >
                            <Text style={styles.modalItemText}>{type.name}</Text>
                            {value === type.id && (
                              <Text style={styles.modalItemCheck}>✓</Text>
                            )}
                          </TouchableOpacity>
                        ))}
                      </ScrollView>
                    </TouchableOpacity>
                  </TouchableOpacity>
                </Modal>
              </>
            );
          }}
        />
      </View>

      {/* Amount */}
      <View style={styles.field}>
        <Text style={styles.label}>Amount ({currencySymbol}) *</Text>
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

      {/* Description (only for "Other" category) */}
      <Controller
        control={control}
        name={`items.${index}.expense_type_id`}
        render={({ field: { value: expenseTypeId } }) => {
          const selectedType = expenseTypes.find(t => t.id === expenseTypeId);
          const isOther = selectedType?.name?.toLowerCase() === 'other';

          if (!isOther) {
            return null;
          }

          return (
            <Controller
              control={control}
              name={`items.${index}.other_category`}
              render={({ field: { onChange, onBlur, value } }) => (
                <View style={styles.field}>
                  <Text style={styles.label}>Description</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="Enter description for 'Other'"
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value || ''}
                    multiline
                  />
                </View>
              )}
            />
          );
        }}
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
  pickerError: {
    borderColor: '#C62828',
  },
  pickerText: {
    fontSize: 16,
    color: '#333',
  },
  placeholderText: {
    color: '#999',
  },
  errorText: {
    color: '#C62828',
    fontSize: 12,
    marginTop: 4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '70%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  modalClose: {
    fontSize: 24,
    color: '#666',
  },
  modalScrollView: {
    maxHeight: 400,
  },
  modalItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F5',
  },
  modalItemText: {
    fontSize: 16,
    color: '#333',
  },
  modalItemCheck: {
    fontSize: 20,
    color: '#00897B',
  },
});
