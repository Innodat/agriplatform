import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import { useReferenceData } from '../hooks/useReferenceData';
import { PurchaseItemForm } from '../components/PurchaseItemForm';
import { supabase } from '../lib/supabase';
import { createReceipt } from '@agriplatform/shared';

const receiptFormSchema = z.object({
  supplier: z.string().min(1, 'Supplier is required'),
  date: z.string(),
  currency_id: z.number(),
  own_money: z.boolean(),
  items: z.array(z.object({
    expense_type_id: z.number(),
    amount: z.number().positive(),
    other_category: z.string().optional(),
  })).min(1, 'At least one item is required'),
});

type ReceiptFormData = z.infer<typeof receiptFormSchema>;

export function AddReceiptScreen({ navigation }: any) {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const { currencies, expenseTypes, loading: refLoading } = useReferenceData();

  const { control, handleSubmit, watch, formState: { errors } } = useForm<ReceiptFormData>({
    resolver: zodResolver(receiptFormSchema),
    defaultValues: {
      supplier: '',
      date: new Date().toISOString().split('T')[0],
      currency_id: currencies[0]?.id || 1,
      own_money: false,
      items: [{ expense_type_id: 0, amount: 0, other_category: '' }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const items = watch('items');
  const totalAmount = items.reduce((sum, item) => sum + (item.amount || 0), 0);

  const handleCameraCapture = async () => {
    const result = await launchCamera({
      mediaType: 'photo',
      quality: 0.8,
    });

    if (result.assets && result.assets[0]) {
      setImageUri(result.assets[0].uri || null);
    }
  };

  const handleGallerySelect = async () => {
    const result = await launchImageLibrary({
      mediaType: 'photo',
      quality: 0.8,
    });

    if (result.assets && result.assets[0]) {
      setImageUri(result.assets[0].uri || null);
    }
  };

  const onSubmit = async (data: ReceiptFormData) => {
    try {
      setSaving(true);

      // Create receipt
      const { data: receipt, error: receiptError } = await createReceipt(supabase, {
        supplier: data.supplier,
      });

      if (receiptError || !receipt) {
        throw new Error(receiptError?.message || 'Failed to create receipt');
      }

      // Create purchases
      for (const item of data.items) {
        const { error: purchaseError } = await supabase
          .schema('finance')
          .from('purchase')
          .insert({
            receipt_id: receipt.id,
            expense_type_id: item.expense_type_id,
            amount: item.amount,
            other_category: item.other_category,
            currency_id: data.currency_id,
            reimbursable: data.own_money,
            captured_timestamp: new Date().toISOString(),
          });

        if (purchaseError) {
          throw new Error(purchaseError.message);
        }
      }

      Alert.alert('Success', 'Receipt saved successfully', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to save receipt');
    } finally {
      setSaving(false);
    }
  };

  if (refLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#00897B" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backButton}>← Add Receipt</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* Receipt Image */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Receipt Image</Text>
          <View style={styles.imageButtons}>
            <TouchableOpacity style={styles.imageButton} onPress={handleCameraCapture}>
              <Text style={styles.imageButtonIcon}>📷</Text>
              <Text style={styles.imageButtonText}>Scan with Camera</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.imageButton} onPress={handleGallerySelect}>
              <Text style={styles.imageButtonIcon}>📁</Text>
              <Text style={styles.imageButtonText}>Choose from Photos</Text>
            </TouchableOpacity>
          </View>
          {imageUri && (
            <Text style={styles.imageSelected}>Image selected ✓</Text>
          )}
        </View>

        {/* Date and Currency */}
        <View style={styles.row}>
          <View style={[styles.field, styles.fieldHalf]}>
            <Text style={styles.label}>Date</Text>
            <TextInput
              style={styles.input}
              value={watch('date')}
              editable={false}
            />
          </View>
          <View style={[styles.field, styles.fieldHalf]}>
            <Text style={styles.label}>Currency</Text>
            <View style={styles.pickerContainer}>
              <Text style={styles.pickerText}>
                {currencies.find(c => c.id === watch('currency_id'))?.symbol || '₹'}
              </Text>
            </View>
          </View>
        </View>

        {/* Supplier */}
        <View style={styles.field}>
          <Text style={styles.label}>Supplier *</Text>
          <TextInput
            style={[styles.input, errors.supplier && styles.inputError]}
            placeholder="Enter supplier name"
            onChangeText={(text) => control._formValues.supplier = text}
          />
          {errors.supplier && (
            <Text style={styles.errorText}>{errors.supplier.message}</Text>
          )}
        </View>

        {/* Own Money Checkbox */}
        <TouchableOpacity
          style={styles.checkbox}
          onPress={() => control._formValues.own_money = !watch('own_money')}
        >
          <View style={[styles.checkboxBox, watch('own_money') && styles.checkboxChecked]}>
            {watch('own_money') && <Text style={styles.checkboxCheck}>✓</Text>}
          </View>
          <Text style={styles.checkboxLabel}>Own money (reimbursable)</Text>
        </TouchableOpacity>

        {/* Purchase Items */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Purchase Items</Text>
            <TouchableOpacity
              style={styles.addItemButton}
              onPress={() => append({ expense_type_id: 0, amount: 0, other_category: '' })}
            >
              <Text style={styles.addItemText}>+ Add Item</Text>
            </TouchableOpacity>
          </View>

          {fields.map((field, index) => (
            <PurchaseItemForm
              key={field.id}
              index={index}
              control={control}
              expenseTypes={expenseTypes}
              onRemove={() => remove(index)}
              showRemove={fields.length > 1}
            />
          ))}
        </View>

        {/* Total Amount */}
        <View style={styles.totalContainer}>
          <Text style={styles.totalLabel}>Total Amount:</Text>
          <Text style={styles.totalAmount}>
            {currencies.find(c => c.id === watch('currency_id'))?.symbol || '₹'}
            {totalAmount.toFixed(2)}
          </Text>
        </View>

        {/* Save Button */}
        <TouchableOpacity
          style={[styles.saveButton, saving && styles.saveButtonDisabled]}
          onPress={handleSubmit(onSubmit)}
          disabled={saving}
        >
          {saving ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.saveButtonText}>💾 Save Receipt</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    padding: 16,
    backgroundColor: '#00897B',
  },
  backButton: {
    fontSize: 18,
    color: '#fff',
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  imageButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  imageButton: {
    flex: 1,
    borderWidth: 2,
    borderColor: '#ddd',
    borderStyle: 'dashed',
    borderRadius: 8,
    padding: 24,
    alignItems: 'center',
  },
  imageButtonIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  imageButtonText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  imageSelected: {
    marginTop: 8,
    color: '#4CAF50',
    fontSize: 14,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  field: {
    marginBottom: 16,
  },
  fieldHalf: {
    flex: 1,
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
  checkbox: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  checkboxBox: {
    width: 24,
    height: 24,
    borderWidth: 2,
    borderColor: '#ddd',
    borderRadius: 4,
    marginRight: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: '#00897B',
    borderColor: '#00897B',
  },
  checkboxCheck: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  checkboxLabel: {
    fontSize: 16,
    color: '#333',
  },
  addItemButton: {
    padding: 8,
  },
  addItemText: {
    color: '#00897B',
    fontSize: 14,
    fontWeight: '500',
  },
  totalContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    marginBottom: 24,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  totalAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#00897B',
  },
  saveButton: {
    backgroundColor: '#00897B',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 24,
  },
  saveButtonDisabled: {
    backgroundColor: '#B2DFDB',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
