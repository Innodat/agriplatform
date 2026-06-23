import React, { useState, useEffect } from 'react';
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
  Image
} from 'react-native';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../navigation/RootNavigator';
import { useReferenceData } from '../hooks/useReferenceData';
import { PurchaseItemForm } from '../components/PurchaseItemForm';
import { BottomSheetPicker } from '../components/BottomSheetPicker';
import { DatePickerField } from '../components/DatePickerField';
import { ImagePickerBottomSheet } from '../components/ImagePickerBottomSheet';
import { FullScreenImageViewer } from '../components/FullScreenImageViewer';
import { supabase, supabaseUrl } from '../lib/supabase';
import { uploadImage } from '../services/content/content.service';
import { useAuth } from '../contexts/AuthContext';
import * as Icon from 'lucide-react-native';

const receiptFormSchema = z.object({
  supplier: z.string().min(1, 'Supplier is required'),
  date: z.string(),
  currency_id: z.number(),
  own_money: z.boolean(),
  items: z.array(z.object({
    expense_type_id: z.number().min(1, 'Expense type is required'),
    amount: z.number().positive('Amount must be greater than 0'),
    other_category: z.string().optional(),
  })).min(1, 'At least one item is required'),
});

type ReceiptFormData = z.infer<typeof receiptFormSchema>;
type AddReceiptScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'AddReceipt'>;

export function AddReceiptScreen() {
  const navigation = useNavigation<AddReceiptScreenNavigationProp>();
  const { session } = useAuth();
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showCurrencyPicker, setShowCurrencyPicker] = useState(false);
  const [showImagePicker, setShowImagePicker] = useState(false);
  const [showFullScreenViewer, setShowFullScreenViewer] = useState(false);
  const { currencies, expenseTypes, loading: refLoading } = useReferenceData();

  const { control, handleSubmit, watch, setValue, formState: { errors } } = useForm<ReceiptFormData>({
    resolver: zodResolver(receiptFormSchema),
    defaultValues: {
      supplier: '',
      date: new Date().toISOString().split('T')[0],
      currency_id: 1, // Default to Zambian Kwacha
      own_money: false,
      items: [{ expense_type_id: 0, amount: 0, other_category: '' }],
    },
  });

  // Set default currency to Zambian Kwacha (id=1) when currencies load
  useEffect(() => {
    if (currencies.length > 0 && !watch('currency_id')) {
      setValue('currency_id', 1);
    }
  }, [currencies, setValue, watch]);

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const items = watch('items');
  const currencyId = watch('currency_id');
  const selectedCurrency = currencies.find(c => c.id === currencyId);
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
  
  type RpcRow = {
    receipt_id: number;
    receipt: unknown;
    purchases: unknown;
  };

  const onSubmit = async (data: ReceiptFormData) => {
    try {
      setSaving(true);
      let contentId: string | null = null;

      // Upload image if one was captured
      if (imageUri) {
        try {
          setUploadingImage(true);
          setUploadProgress(0);
          
          const uploadResult = await uploadImage(imageUri, {
            supabaseUrl,
            accessToken: session?.access_token ?? '',
            onProgress: (progress) => setUploadProgress(progress),
          });
          
          contentId = uploadResult.contentId;
          console.log('Image uploaded successfully, content_id:', contentId);
        } catch (uploadError) {
          console.error('Image upload failed:', uploadError);
          // Ask user if they want to continue without the image
          const shouldContinue = await new Promise<boolean>((resolve) => {
            Alert.alert(
              'Image Upload Failed',
              'Failed to upload the receipt image. Do you want to save the receipt without the image?',
              [
                { text: 'Cancel', style: 'cancel', onPress: () => resolve(false) },
                { text: 'Save Without Image', onPress: () => resolve(true) },
              ]
            );
          });
          
          if (!shouldContinue) {
            setUploadingImage(false);
            setSaving(false);
            return;
          }
        } finally {
          setUploadingImage(false);
        }
      }
  
      // Map form items to the JSON structure expected by jsonb_to_recordset(...)
      // (optional overrides like currency_id/reimbursable/user_id are not sent here)
      const items = data.items.map((it) => ({
        expense_type_id: it.expense_type_id,
        amount: it.amount,
        other_category: it.other_category ?? null,
      }));
  
      const { data: rows, error } = await supabase
        .schema('finance') // function is in a custom schema
        .rpc('create_receipt_with_purchases', {
          p_supplier: data.supplier,
          p_receipt_date: data.date,       // <-- DATE string: 'YYYY-MM-DD'
          p_currency_id: data.currency_id,
          p_reimbursable: data.own_money,
          p_content_id: contentId,          // <-- NEW: content_id from image upload
          p_items: items,
        });
  
      if (error) throw error;
  
      const row = (rows as RpcRow[] | null)?.[0];
      if (!row) throw new Error('No data returned from function');
  
      // Optional: validate result shape if you want extra safety
      // const parsed = purchaseRowSchema.array().safeParse(row.purchases);
      // if (!parsed.success) throw new Error(parsed.error.message);
  
      Alert.alert('Success', 'Receipt saved successfully', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (err) {
      Alert.alert(
        'Error',
        err instanceof Error ? err.message : 'Failed to save receipt'
      );
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
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Icon.ChevronLeft size={24} color="#fff" />
          <Text style={styles.backButtonText}>Add Receipt</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* Receipt Image - Modern Design */}
        {imageUri ? (
          <View style={styles.imagePreviewContainer}>
            <TouchableOpacity
              onPress={() => setShowFullScreenViewer(true)}
              activeOpacity={0.9}
              style={styles.imagePreviewTouchable}
            >
              <Image 
                source={{ uri: imageUri }} 
                style={styles.imagePreview} 
                resizeMode="cover"
                onError={(error) => console.log('Image load error:', error.nativeEvent)}
                onLoad={() => console.log('Image loaded successfully')}
              />
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.editImageButton}
              onPress={() => setShowImagePicker(true)}
            >
              <Icon.Pencil size={18} color="#00897B" />
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity
            style={styles.addImageButton}
            onPress={() => setShowImagePicker(true)}
          >
            <View style={styles.addImageIconContainer}>
              <Icon.Camera size={32} color="#6B7280" />
            </View>
            <Text style={styles.addImageText}>Add Receipt Image</Text>
            <Text style={styles.addImageSubtext}>Tap to take photo or choose from gallery</Text>
          </TouchableOpacity>
        )}

        {/* Date and Currency */}
        <View style={styles.row}>
          <View style={[styles.fieldHalf]}>
            <Controller
              control={control}
              name="date"
              render={({ field: { onChange, value } }) => (
                <DatePickerField
                  value={value}
                  onChange={onChange}
                  label="Date"
                />
              )}
            />
          </View>
          <View style={[styles.field, styles.fieldHalf]}>
            <Text style={styles.label}>Currency</Text>
            <Controller
              control={control}
              name="currency_id"
              render={({ field: { value } }) => (
                <TouchableOpacity
                  style={styles.pickerContainer}
                  onPress={() => setShowCurrencyPicker(true)}
                >
                  <Text style={styles.pickerText}>
                    {selectedCurrency?.symbol || 'K'} {selectedCurrency?.name || 'Zambian Kwatchas'}
                  </Text>
                </TouchableOpacity>
              )}
            />
          </View>
        </View>

        {/* Supplier */}
        <View style={styles.field}>
          <Text style={styles.label}>Supplier *</Text>
          <Controller
            control={control}
            name="supplier"
            render={({ field: { onChange, onBlur, value }, fieldState: { error } }) => (
              <>
                <TextInput
                  style={[styles.input, error && styles.inputError]}
                  placeholder="Enter supplier name"
                  onBlur={onBlur}
                  onChangeText={onChange}
                  value={value}
                />
                {error && <Text style={styles.errorText}>{error.message}</Text>}
              </>
            )}
          />
        </View>

        {/* Own Money Checkbox */}
        <Controller
          control={control}
          name="own_money"
          render={({ field: { onChange, value } }) => (
            <TouchableOpacity
              style={styles.checkbox}
              onPress={() => onChange(!value)}
            >
              <View style={[styles.checkboxBox, value && styles.checkboxChecked]}>
                {value && <Icon.Check size={16} color="#fff" />}
              </View>
              <Text style={styles.checkboxLabel}>Own money (reimbursable)</Text>
            </TouchableOpacity>
          )}
        />

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
              currencySymbol={selectedCurrency?.symbol || 'K'}
            />
          ))}
        </View>

        {/* Total Amount */}
        <View style={styles.totalContainer}>
          <Text style={styles.totalLabel}>Total Amount:</Text>
          <Text style={styles.totalAmount}>
            {selectedCurrency?.symbol || 'K'}
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
            <View style={styles.saveButtonContent}>
              <Icon.Check size={20} color="#fff" />
              <Text style={styles.saveButtonText}>Save Receipt</Text>
            </View>
          )}
        </TouchableOpacity>
      </ScrollView>

      {/* Currency Picker */}
      <BottomSheetPicker
        visible={showCurrencyPicker}
        title="Select Currency"
        items={currencies.map(c => ({ id: c.id, name: c.name, symbol: c.symbol || '' }))}
        selectedId={currencyId}
        onSelect={(id) => setValue('currency_id', id)}
        onClose={() => setShowCurrencyPicker(false)}
        searchPlaceholder="Search currencies..."
      />

      {/* Image Picker Bottom Sheet */}
      <ImagePickerBottomSheet
        visible={showImagePicker}
        onClose={() => setShowImagePicker(false)}
        onTakePhoto={handleCameraCapture}
        onChooseFromGallery={handleGallerySelect}
      />

      {/* Full Screen Image Viewer */}
      <FullScreenImageViewer
        visible={showFullScreenViewer}
        imageUri={imageUri}
        onClose={() => setShowFullScreenViewer(false)}
        onReplace={() => setShowImagePicker(true)}
        onDelete={() => setImageUri(null)}
      />
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
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButtonText: {
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
  // Modern Image Picker Styles
  addImageButton: {
    backgroundColor: '#F8F9FA',
    borderRadius: 16,
    padding: 32,
    alignItems: 'center',
    marginBottom: 24,
    borderWidth: 2,
    borderColor: '#E0E0E0',
    borderStyle: 'dashed',
  },
  addImageIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  addImageIcon: {
    fontSize: 32,
  },
  addImageText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  addImageSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  imagePreviewContainer: {
    position: 'relative',
    marginBottom: 24,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: '#F5F5F5',
    minHeight: 200,
  },
  imagePreviewTouchable: {
    width: '100%',
    height: 200,
  },
  imagePreview: {
    width: '100%',
    height: 200,
  },
  editImageButton: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
    zIndex: 10,
  },
  editImageIcon: {
    fontSize: 20,
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
  saveButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
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
    maxHeight: '60%',
    minHeight: 300,
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
