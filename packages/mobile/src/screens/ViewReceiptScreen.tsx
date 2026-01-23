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
import { ContextMenu, ContextMenuItem } from '../components/ContextMenu';
import { supabase, supabaseUrl } from '../lib/supabase';
import { uploadImage } from '../services/content/content.service';
import { useAuth } from '../contexts/AuthContext';
import * as Icon from 'lucide-react-native';
import { format, isToday } from 'date-fns';

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
    status: z.enum(['pending', 'approved', 'rejected', 'querying']).optional(),
  })).min(1, 'At least one item is required'),
});

type ReceiptFormData = z.infer<typeof receiptFormSchema>;
type ViewReceiptScreenRouteProp = RouteProp<RootStackParamList, 'ViewReceipt'>;
type ViewReceiptScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'ViewReceipt'>;

interface PurchaseData {
  id: number;
  expense_type_id: number;
  amount: string;
  other_category: string | null;
  currency_id: number;
  reimbursable: boolean;
  status: 'pending' | 'approved' | 'rejected' | 'querying';
}

interface ReceiptWithPurchases {
  id: number;
  supplier: string | null;
  receipt_date: string | null;
  content_id: string | null;
  purchases: PurchaseData[];
}

export function ViewReceiptScreen() {
  const route = useRoute<ViewReceiptScreenRouteProp>();
  const navigation = useNavigation<ViewReceiptScreenNavigationProp>();
  const { session } = useAuth();
  const { receiptId } = route.params;
  
  // View/Edit mode state
  const [isEditMode, setIsEditMode] = useState(false);
  
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
  const [showMoreMenu, setShowMoreMenu] = useState(false);
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [existingContentId, setExistingContentId] = useState<string | null>(null);
  const [imageChanged, setImageChanged] = useState(false);
  
  const { currencies, expenseTypes, loading: refLoading } = useReferenceData();

  const { control, handleSubmit, watch, setValue, reset, formState: { errors, isDirty } } = useForm<ReceiptFormData>({
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
    
    // Check if receipt is from today
    const today = new Date().toISOString().split('T')[0];
    const isReceiptToday = receipt.receipt_date === today;
    if (!isReceiptToday) return false;
    
    // Check if any item is approved/rejected
    const hasApprovedOrRejected = receipt.purchases.some(
      p => p.status === 'approved' || p.status === 'rejected'
    );
    if (hasApprovedOrRejected) return false;
    
    return true;
  }, [receipt]);

  // Check if delete is allowed
  const canDelete = useCallback(() => {
    if (!receipt) return false;
    return !receipt.purchases.some(
      p => p.status === 'approved' || p.status === 'rejected'
    );
  }, [receipt]);

  // Get edit restriction reason
  const getEditRestrictionReason = useCallback(() => {
    if (!receipt) return '';
    
    const today = new Date().toISOString().split('T')[0];
    const isReceiptToday = receipt.receipt_date === today;
    
    if (!isReceiptToday) {
      return 'Cannot edit receipts from previous days';
    }
    
    const hasApprovedOrRejected = receipt.purchases.some(
      p => p.status === 'approved' || p.status === 'rejected'
    );
    
    if (hasApprovedOrRejected) {
      return 'Cannot edit - some items have been approved or rejected';
    }
    
    return '';
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
      
      setValue('items', purchases.map((p: any) => ({
        id: p.id,
        expense_type_id: p.expense_type_id,
        amount: Number(p.amount),
        other_category: p.other_category || '',
        status: p.status,
      })));
      
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load receipt');
    } finally {
      setLoading(false);
    }
  };

  const handleEditPress = () => {
    if (canEdit()) {
      setIsEditMode(true);
    } else {
      Alert.alert('Cannot Edit', getEditRestrictionReason());
    }
  };

  const handleCancelEdit = () => {
    if (isDirty) {
      Alert.alert(
        'Discard Changes?',
        'You have unsaved changes. Are you sure you want to discard them?',
        [
          { text: 'Keep Editing', style: 'cancel' },
          { 
            text: 'Discard', 
            style: 'destructive',
            onPress: () => {
              loadReceiptData();
              setIsEditMode(false);
            }
          },
        ]
      );
    } else {
      setIsEditMode(false);
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
              await archiveReceipt(supabase as any, receiptId);
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
        } catch (uploadError) {
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
        contentId = null;
      }

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

      await syncPurchases(data);

      Alert.alert('Success', 'Receipt updated successfully', [
        { text: 'OK', onPress: () => {
          setIsEditMode(false);
          loadReceiptData();
        }},
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

    const toDelete = originalIds.filter(id => !existingIds.includes(id));
    for (const id of toDelete) {
      const { error } = await supabase
        .schema('finance')
        .from('purchase')
        .update({ is_active: false })
        .eq('id', id);
      if (error) throw new Error(error.message);
    }

    for (const item of data.items) {
      if (item.status === 'approved' || item.status === 'rejected') {
        continue;
      }

      if (item.id) {
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

  // More menu items
  const moreMenuItems: ContextMenuItem[] = [
    ...(canEdit() ? [{
      id: 'edit',
      label: 'Edit Receipt',
      icon: 'edit-2',
      onPress: handleEditPress,
    }] : []),
    ...(canDelete() ? [{
      id: 'delete',
      label: 'Delete Receipt',
      icon: 'trash-2',
      onPress: handleDelete,
      destructive: true,
    }] : []),
  ];

  // Loading state
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

  // Error state
  if (loadError) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorScreen}>
          <Icon.AlertCircle size={64} color="#DC2626" />
          <Text style={styles.errorTitle}>Failed to Load Receipt</Text>
          <Text style={styles.errorMessage}>{loadError}</Text>
          <TouchableOpacity
            style={styles.goBackButton}
            onPress={() => navigation.goBack()}
          >
            <Icon.ChevronLeft size={20} color="#fff" />
            <Text style={styles.goBackButtonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const receiptDate = receipt?.receipt_date ? new Date(receipt.receipt_date) : new Date();
  const formattedDate = format(receiptDate, 'dd MMMM yyyy');
  const isTodayReceipt = receipt?.receipt_date ? isToday(receiptDate) : false;

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          onPress={() => navigation.goBack()} 
          style={styles.backButton}
        >
          <Icon.ChevronLeft size={24} color="#fff" />
          <Text style={styles.headerTitle}>
            {isEditMode ? 'Edit Receipt' : 'Receipt Details'}
          </Text>
        </TouchableOpacity>
        
        <View style={styles.headerActions}>
          {isEditMode ? (
            <>
              <TouchableOpacity 
                onPress={handleCancelEdit}
                style={styles.headerButton}
              >
                <Icon.X size={24} color="#fff" />
              </TouchableOpacity>
              <TouchableOpacity 
                onPress={handleSubmit(onSubmit)}
                style={styles.headerButton}
                disabled={saving}
              >
                {saving ? (
                  <ActivityIndicator size="small" color="#fff" />
                ) : (
                  <Icon.Check size={24} color="#fff" />
                )}
              </TouchableOpacity>
            </>
          ) : (
            <>
              <TouchableOpacity 
                onPress={handleEditPress}
                style={[
                  styles.headerButton,
                  !canEdit() && styles.headerButtonDisabled
                ]}
              >
                <Icon.Pencil 
                  size={22} 
                  color={canEdit() ? '#fff' : 'rgba(255,255,255,0.5)'} 
                />
              </TouchableOpacity>
              <TouchableOpacity 
                onPress={() => setShowMoreMenu(true)}
                style={styles.headerButton}
              >
                <Icon.MoreVertical size={22} color="#fff" />
              </TouchableOpacity>
            </>
          )}
        </View>
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
            {isEditMode && (
              <TouchableOpacity
                style={styles.editImageButton}
                onPress={() => setShowImagePicker(true)}
              >
                <Icon.Pencil size={18} color="#00897B" />
              </TouchableOpacity>
            )}
          </View>
        ) : isEditMode ? (
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
        ) : (
          <View style={styles.noImageContainer}>
            <Icon.Image size={48} color="#D1D5DB" />
            <Text style={styles.noImageText}>No image attached</Text>
          </View>
        )}

        {/* Date Badge */}
        <View style={styles.dateBadgeContainer}>
          <View style={[styles.dateBadge, isTodayReceipt && styles.dateBadgeToday]}>
            <Icon.Calendar size={16} color={isTodayReceipt ? '#10B981' : '#6B7280'} />
            <Text style={[styles.dateBadgeText, isTodayReceipt && styles.dateBadgeTextToday]}>
              {formattedDate}
              {isTodayReceipt && ' (Today)'}
            </Text>
          </View>
        </View>

        {/* Supplier */}
        <View style={styles.field}>
          <Text style={styles.label}>Supplier</Text>
          {isEditMode ? (
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
          ) : (
            <Text style={styles.valueText}>{watch('supplier') || 'Not specified'}</Text>
          )}
        </View>

        {/* Currency */}
        <View style={styles.field}>
          <Text style={styles.label}>Currency</Text>
          {isEditMode ? (
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
                  <Icon.ChevronDown size={20} color="#6B7280" />
                </TouchableOpacity>
              )}
            />
          ) : (
            <Text style={styles.valueText}>
              {selectedCurrency?.symbol || 'K'} {selectedCurrency?.name || 'Zambian Kwacha'}
            </Text>
          )}
        </View>

        {/* Own Money Checkbox */}
        <Controller
          control={control}
          name="own_money"
          render={({ field: { onChange, value } }) => (
            <TouchableOpacity
              style={styles.checkbox}
              onPress={() => isEditMode && onChange(!value)}
              disabled={!isEditMode}
            >
              <View style={[
                styles.checkboxBox, 
                value && styles.checkboxChecked,
                !isEditMode && styles.checkboxDisabled
              ]}>
                {value && <Icon.Check size={16} color="#fff" />}
              </View>
              <Text style={[styles.checkboxLabel, !isEditMode && styles.checkboxLabelDisabled]}>
                Own money (reimbursable)
              </Text>
            </TouchableOpacity>
          )}
        />

        {/* Purchase Items */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Purchase Items</Text>
            {isEditMode && canEdit() && (
              <TouchableOpacity
                style={styles.addItemButton}
                onPress={() => append({ expense_type_id: 0, amount: 0, other_category: '' })}
              >
                <Icon.Plus size={16} color="#00897B" />
                <Text style={styles.addItemText}>Add Item</Text>
              </TouchableOpacity>
            )}
          </View>

          {fields.map((field, index) => {
            const item = items[index];
            const isReadOnly = !isEditMode || item.status === 'approved' || item.status === 'rejected';
            
            return (
              <PurchaseItemForm
                key={field.id}
                index={index}
                control={control}
                expenseTypes={expenseTypes}
                onRemove={() => remove(index)}
                showRemove={isEditMode && fields.length > 1 && !isReadOnly}
                currencySymbol={selectedCurrency?.symbol || 'K'}
                readOnly={isReadOnly}
              />
            );
          })}
        </View>

        {/* Total Amount */}
        <View style={styles.totalContainer}>
          <Text style={styles.totalLabel}>Total Amount</Text>
          <Text style={styles.totalAmount}>
            {selectedCurrency?.symbol || 'K'}
            {totalAmount.toFixed(2)}
          </Text>
        </View>

        {/* Delete Button (View Mode Only) */}
        {!isEditMode && canDelete() && (
          <TouchableOpacity
            style={[styles.deleteButton, deleting && styles.deleteButtonDisabled]}
            onPress={handleDelete}
            disabled={deleting}
          >
            {deleting ? (
              <ActivityIndicator color="#DC2626" />
            ) : (
              <>
                <Icon.Trash2 size={20} color="#DC2626" />
                <Text style={styles.deleteButtonText}>Delete Receipt</Text>
              </>
            )}
          </TouchableOpacity>
        )}

        <View style={styles.bottomSpacer} />
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
        onReplace={isEditMode ? (() => setShowImagePicker(true)) : (() => {})}
        onDelete={isEditMode ? (() => {
          setImageUri(null);
          setImageChanged(true);
          setShowFullScreenViewer(false);
        }) : (() => {})}
      />

      {/* More Menu */}
      <ContextMenu
        visible={showMoreMenu}
        items={moreMenuItems}
        onClose={() => setShowMoreMenu(false)}
        title={receipt?.supplier || 'Receipt Options'}
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#00897B',
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginLeft: 8,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerButton: {
    padding: 8,
  },
  headerButtonDisabled: {
    opacity: 0.5,
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
  errorTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1F2937',
    marginTop: 16,
    marginBottom: 8,
  },
  errorMessage: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 24,
  },
  goBackButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#00897B',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    gap: 8,
  },
  goBackButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  // Image styles
  imagePreviewContainer: {
    position: 'relative',
    marginBottom: 16,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#F3F4F6',
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
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
  },
  addImageButton: {
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    padding: 32,
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#E5E7EB',
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
  addImageText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  addImageSubtext: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
  },
  noImageContainer: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 32,
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  noImageText: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8,
  },
  dateBadgeContainer: {
    marginBottom: 16,
  },
  dateBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 6,
  },
  dateBadgeToday: {
    backgroundColor: '#ECFDF5',
  },
  dateBadgeText: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  dateBadgeTextToday: {
    color: '#10B981',
  },
  field: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 6,
  },
  input: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
    color: '#1F2937',
  },
  inputError: {
    borderColor: '#DC2626',
  },
  valueText: {
    fontSize: 16,
    color: '#1F2937',
    paddingVertical: 4,
  },
  pickerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#fff',
  },
  pickerText: {
    fontSize: 16,
    color: '#1F2937',
  },
  errorText: {
    color: '#DC2626',
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
    borderColor: '#D1D5DB',
    borderRadius: 4,
    marginRight: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: '#00897B',
    borderColor: '#00897B',
  },
  checkboxDisabled: {
    backgroundColor: '#F3F4F6',
  },
  checkboxLabel: {
    fontSize: 16,
    color: '#374151',
  },
  checkboxLabelDisabled: {
    color: '#9CA3AF',
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
    color: '#1F2937',
  },
  addItemButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
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
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    marginBottom: 24,
  },
  totalLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  totalAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#00897B',
  },
  deleteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#FEF2F2',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FECACA',
    marginBottom: 16,
  },
  deleteButtonDisabled: {
    opacity: 0.5,
  },
  deleteButtonText: {
    color: '#DC2626',
    fontSize: 16,
    fontWeight: '600',
  },
  bottomSpacer: {
    height: 32,
  },
});