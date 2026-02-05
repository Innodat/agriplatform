import React, { useState, useEffect, useCallback } from 'react';
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
  Image,
} from 'react-native';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../navigation/RootNavigator';
import { useReferenceData } from '../hooks/useReferenceData';
import { getReceiptById, archiveReceipt } from '@agriplatform/shared';
import { PurchaseItemForm } from '../components/PurchaseItemForm';
import { BottomSheetPicker } from '../components/BottomSheetPicker';
import { ImagePickerBottomSheet } from '../components/ImagePickerBottomSheet';
import { FullScreenImageViewer } from '../components/FullScreenImageViewer';
import { supabase, supabaseUrl } from '../lib/supabase';
import { uploadImage } from '../services/content/content.service';
import { useAuth } from '../contexts/AuthContext';

const receiptFormSchema = z.object({
  supplier: z.string().min(1, 'Supplier is required'),
  date: z.string(),
  currency_id: z.number(),
  own_money: z.boolean(),
  items: z.array(z.object({
    id: z.number().optional(),
    expense_type_id: z.number().min(1, 'Expense type is required'),
    amount: z.number().positive('Amount must be greater than 0'),
    other_category: z.string().optional(),
  })).min(1, 'At least one item is required'),
});

type ReceiptFormData = z.infer<typeof receiptFormSchema>;
type EditReceiptScreenRouteProp = RouteProp<RootStackParamList, 'EditReceipt'>;
type EditReceiptScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'EditReceipt'>;

interface PurchaseData {
  id: number;
  expense_type_id: number;
  amount: string;
  other_category: string | null;
  currency_id: number;
  reimbursable: boolean;
}

interface ReceiptWithPurchases {
  id: number;
  supplier: string | null;
  receipt_date: string | null;
  content_id: string | null;
  status: 'pending' | 'approved' | 'rejected' | 'querying';
  purchases: PurchaseData[];
}

const canModifyReceipt = (status?: string | null) =>
  status === 'pending' || status === 'querying';

export function EditReceiptScreen() {
  const route = useRoute<EditReceiptScreenRouteProp>();
  const navigation = useNavigation<EditReceiptScreenNavigationProp>();
  const { session } = useAuth();
  const { receiptId } = route.params;
  
  const [receipt, setReceipt] = useState<ReceiptWithPurchases | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showCurrencyPicker, setShowCurrencyPicker] = useState(false);
  const [showImagePicker, setShowImagePicker] = useState(false);
  const [showFullScreenViewer, setShowFullScreenViewer] = useState(false);
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [existingContentId, setExistingContentId] = useState<string | null>(null);
  const [imageChanged, setImageChanged] = useState(false);
  
  const { currencies, expenseTypes, loading: refLoading } = useReferenceData();

  const { control, handleSubmit, watch, setValue, formState: { errors } } = useForm<ReceiptFormData>({
    resolver: zodResolver(receiptFormSchema),
    defaultValues: {
      supplier: '',
      date: new Date().toISOString().split('T')[0],
      currency_id: 1,
      own_money: false,
      items: [{ expense_type_id: 0, amount: 0, other_category: '' }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const items = watch('items');
  const currencyId = watch('currency_id');
  const selectedCurrency = currencies.find(c => c.id === currencyId);
  const totalAmount = items.reduce((sum, item) => sum + (item.amount || 0), 0);

  // Check if receipt is editable
  const canEdit = useCallback(() => {
    if (!receipt) return false;
    return canModifyReceipt(receipt.status);
  }, [receipt]);

  // Check if delete is allowed
  const canDelete = useCallback(() => {
    if (!receipt) return false;
    return canModifyReceipt(receipt.status);
  }, [receipt]);

  // Load receipt data
  useEffect(() => {
    loadReceiptData();
  }, [receiptId]);

  const loadReceiptData = async () => {
    try {
      setLoading(true);
      setLoadError(null);
      
      const result = await getReceiptById(supabase as any, receiptId);
      
      if (result.error) {
        throw new Error(result.error.message);
      }
      
      if (!result.data) {
        throw new Error('Receipt not found');
      }
      
      const data = result.data as any;
      setReceipt(data);
      
      // Load existing image if content_id exists
      if (data.content_id) {
        try {
          // Generate signed URL for existing image
          const response = await fetch(
            `${supabaseUrl}/functions/v1/cs-generate-signed-url?id=${data.content_id}`,
            {
              method: 'GET',
              headers: {
                'Authorization': `Bearer ${session?.access_token}`,
              },
            }
          );
          
          if (response.ok) {
            const result = await response.json();
            if (result.signed_url) {
              setExistingContentId(data.content_id);
              setImageUri(result.signed_url);
            }
          } else {
            console.error('Failed to generate signed URL:', await response.text());
          }
        } catch (err) {
          console.error('Failed to load image:', err);
        }
      }
      
      // Pre-populate form
      setValue('supplier', data.supplier || '');
      setValue('date', data.receipt_date || new Date().toISOString().split('T')[0]);
      
      const purchases = data.purchases || [];
      if (purchases.length > 0) {
        setValue('currency_id', purchases[0]?.currency_id || 1);
        setValue('own_money', purchases[0]?.reimbursable || false);
      }
      
      // Set items
      setValue('items', purchases.map((p: any) => ({
        id: p.id,
        expense_type_id: p.expense_type_id,
        amount: Number(p.amount),
        other_category: p.other_category || '',
      })));
      
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load receipt');
    } finally {
      setLoading(false);
    }
  };

  const handleCameraCapture = async () => {
    const result = await launchCamera({
      mediaType: 'photo',
      quality: 0.8,
    });

    if (result.assets && result.assets[0]) {
      setImageUri(result.assets[0].uri || null);
      setImageChanged(true);
    }
  };

  const handleGallerySelect = async () => {
    const result = await launchImageLibrary({
      mediaType: 'photo',
      quality: 0.8,
    });

    if (result.assets && result.assets[0]) {
      setImageUri(result.assets[0].uri || null);
      setImageChanged(true);
    }
  };

  const handleDelete = async () => {
    Alert.alert(
      'Delete Receipt',
      'Are you sure you want to delete this receipt? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              setDeleting(true);
              const { error } = await archiveReceipt(supabase as any, receiptId);
              if (error) {
                throw new Error(error.message);
              }
              Alert.alert('Success', 'Receipt deleted successfully', [
                { text: 'OK', onPress: () => navigation.goBack() },
              ]);
            } catch (err) {
              Alert.alert(
                'Error',
                err instanceof Error ? err.message : 'Failed to delete receipt'
              );
            } finally {
              setDeleting(false);
            }
          },
        },
      ]
    );
  };

  const onSubmit = async (data: ReceiptFormData) => {
    try {
      setSaving(true);
      let contentId = existingContentId;

      // Handle image changes
      if (imageChanged && imageUri) {
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
      } else if (imageChanged && !imageUri) {
        // Image removed
        contentId = null;
      }

      // Update receipt
      const { error: updateError } = await supabase
        .schema('finance')
        .from('receipt')
        .update({
          supplier: data.supplier,
          content_id: contentId,
          updated_by: session?.user?.id,
          updated_at: new Date().toISOString(),
        })
        .eq('id', receiptId);

      if (updateError) throw new Error(updateError.message);

      // Sync purchases
      await syncPurchases(data);

      Alert.alert('Success', 'Receipt updated successfully', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (err) {
      Alert.alert(
        'Error',
        err instanceof Error ? err.message : 'Failed to update receipt'
      );
    } finally {
      setSaving(false);
    }
  };

  const syncPurchases = async (data: ReceiptFormData) => {
    const existingIds = data.items.filter(i => i.id).map(i => i.id!);
    const originalIds = receipt?.purchases.map(p => p.id) || [];

    // Delete removed items
    const toDelete = originalIds.filter(id => !existingIds.includes(id));
    for (const id of toDelete) {
      const { error } = await supabase
        .schema('finance')
        .from('purchase')
        .update({ deleted_at: new Date().toISOString() })
        .eq('id', id);
      if (error) throw new Error(error.message);
    }

    // Update or insert items
    for (const item of data.items) {
      if (item.id) {
        // Update existing
        const { error } = await supabase
          .schema('finance')
          .from('purchase')
          .update({
            expense_type_id: item.expense_type_id,
            amount: item.amount,
            other_category: item.other_category || null,
            reimbursable: data.own_money,
            currency_id: data.currency_id,
            updated_by: session?.user?.id,
            updated_at: new Date().toISOString(),
          })
          .eq('id', item.id);
        if (error) throw new Error(error.message);
      } else {
        // Insert new
        const { error } = await supabase
          .schema('finance')
          .from('purchase')
          .insert({
            receipt_id: receiptId,
            expense_type_id: item.expense_type_id,
            amount: item.amount,
            other_category: item.other_category || null,
            reimbursable: data.own_money,
            currency_id: data.currency_id,
            user_id: session?.user?.id,
            created_by: session?.user?.id,
            updated_by: session?.user?.id,
          });
        if (error) throw new Error(error.message);
      }
    }
  };

  // Show loading state
  if (loading || refLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#00897B" />
          <Text style={styles.loadingText}>Loading receipt...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Show error state
  if (loadError) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorScreen}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorTitle}>Failed to Load Receipt</Text>
          <Text style={styles.errorMessage}>{loadError}</Text>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>← Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // Show cannot edit message
  if (!canEdit()) {
    const canModify = receipt ? canModifyReceipt(receipt.status) : false;

    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Text style={styles.backButtonText}>← Edit Receipt</Text>
          </TouchableOpacity>
        </View>
        <ScrollView style={styles.content}>
          <View style={styles.cannotEditContainer}>
            <Text style={styles.cannotEditIcon}>🔒</Text>
            <Text style={styles.cannotEditTitle}>Cannot Edit Receipt</Text>
            <View style={styles.cannotEditReasons}>
              {!canModify && (
                <Text style={styles.cannotEditReason}>
                  • Receipt can only be edited or deleted when status is pending or querying
                </Text>
              )}
            </View>
            <TouchableOpacity
              style={styles.goBackButton}
              onPress={() => navigation.goBack()}
            >
              <Text style={styles.goBackButtonText}>← Go Back to Receipts</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backButtonText}>← Edit Receipt</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* Receipt Image */}
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
              />
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.editImageButton}
              onPress={() => setShowImagePicker(true)}
            >
              <Text style={styles.editImageIcon}>✏️</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity
            style={styles.addImageButton}
            onPress={() => setShowImagePicker(true)}
          >
            <View style={styles.addImageIconContainer}>
              <Text style={styles.addImageIcon}>📷</Text>
            </View>
            <Text style={styles.addImageText}>Add Receipt Image</Text>
            <Text style={styles.addImageSubtext}>Tap to take photo or choose from gallery</Text>
          </TouchableOpacity>
        )}

        {/* Date and Currency */}
        <View style={styles.row}>
          <View style={[styles.fieldHalf]}>
            <Text style={styles.label}>Date</Text>
            <View style={styles.readOnlyContainer}>
              <Text style={styles.readOnlyText}>
                {watch('date') || 'Not set'}
              </Text>
              <Text style={styles.readOnlyNote}>Cannot change receipt date</Text>
            </View>
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
                    {selectedCurrency?.symbol || 'K'} {selectedCurrency?.name || 'Zambian Kwacha'}
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
                {value && <Text style={styles.checkboxCheck}>✓</Text>}
              </View>
              <Text style={styles.checkboxLabel}>Own money (reimbursable)</Text>
            </TouchableOpacity>
          )}
        />

        {/* Purchase Items */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Purchase Items</Text>
            {canDelete() && (
              <TouchableOpacity
                style={styles.addItemButton}
                onPress={() => append({ expense_type_id: 0, amount: 0, other_category: '' })}
              >
                <Text style={styles.addItemText}>+ Add Item</Text>
              </TouchableOpacity>
            )}
          </View>

          {fields.map((field, index) => {
            const isReadOnly = !canEdit();
            
            return (
              <PurchaseItemForm
                key={field.id}
                index={index}
                control={control}
                expenseTypes={expenseTypes}
                onRemove={() => remove(index)}
                showRemove={fields.length > 1 && !isReadOnly}
                currencySymbol={selectedCurrency?.symbol || 'K'}
                readOnly={isReadOnly}
              />
            );
          })}
        </View>

        {/* Total Amount */}
        <View style={styles.totalContainer}>
          <Text style={styles.totalLabel}>Total Amount:</Text>
          <Text style={styles.totalAmount}>
            {selectedCurrency?.symbol || 'K'}
            {totalAmount.toFixed(2)}
          </Text>
        </View>

        {/* Action Buttons */}
        <TouchableOpacity
          style={[styles.saveButton, saving && styles.saveButtonDisabled]}
          onPress={handleSubmit(onSubmit)}
          disabled={saving}
        >
          {saving ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.saveButtonText}>💾 Update Receipt</Text>
          )}
        </TouchableOpacity>

        {canDelete() && (
          <TouchableOpacity
            style={[styles.deleteButton, deleting && styles.deleteButtonDisabled]}
            onPress={handleDelete}
            disabled={deleting}
          >
            {deleting ? (
              <ActivityIndicator color="#C62828" />
            ) : (
              <Text style={styles.deleteButtonText}>🗑️ Delete Receipt</Text>
            )}
          </TouchableOpacity>
        )}
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
        onDelete={() => {
          setImageUri(null);
          setImageChanged(true);
          setShowFullScreenViewer(false);
        }}
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
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  errorScreen: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  errorIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  errorTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  errorMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
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
  },
  // Cannot Edit Styles
  cannotEditContainer: {
    padding: 48,
    alignItems: 'center',
  },
  cannotEditIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  cannotEditTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#333',
    marginBottom: 24,
  },
  cannotEditReasons: {
    marginBottom: 32,
  },
  cannotEditReason: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
    textAlign: 'center',
  },
  goBackButton: {
    backgroundColor: '#00897B',
    padding: 16,
    borderRadius: 8,
  },
  goBackButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  // Image Styles
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
  readOnlyContainer: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#F5F5F5',
  },
  readOnlyText: {
    fontSize: 16,
    color: '#666',
  },
  readOnlyNote: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
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
    marginBottom: 12,
  },
  saveButtonDisabled: {
    backgroundColor: '#B2DFDB',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  deleteButton: {
    backgroundColor: '#FFEBEE',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#C62828',
  },
  deleteButtonDisabled: {
    backgroundColor: '#F5F5F5',
    borderColor: '#ddd',
  },
  deleteButtonText: {
    color: '#C62828',
    fontSize: 16,
    fontWeight: '600',
  },
});
