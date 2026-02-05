import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  FlatList,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { useFocusEffect } from '@react-navigation/native';
import * as Icon from 'lucide-react-native';
import { useAuth } from '../contexts/AuthContext';
import { useReceipts } from '../hooks/useReceipts';
import { SwipeableReceiptItem } from '../components/SwipeableReceiptItem';
import { ContextMenu, ContextMenuItem } from '../components/ContextMenu';
import { UndoSnackbar } from '../components/UndoSnackbar';
import { archiveReceipt } from '@agriplatform/shared';
import { supabase } from '../lib/supabase';

interface PendingDelete {
  id: number;
  supplier: string;
}

const canModifyReceipt = (status?: string | null) =>
  status === 'pending' || status === 'querying';

export function ReceiptListScreen({ navigation }: any) {
  const { user, signOut } = useAuth();
  const { receipts, loading, error, refresh, loadMore, hasMore } = useReceipts();
  
  // Context menu state
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [selectedReceipt, setSelectedReceipt] = useState<{ id: number; supplier: string } | null>(null);
  
  // Undo snackbar state
  const [pendingDelete, setPendingDelete] = useState<PendingDelete | null>(null);
  const [showUndoSnackbar, setShowUndoSnackbar] = useState(false);

  // Automatically refresh receipts when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      refresh();
    }, [refresh])
  );

  const handleSignOut = async () => {
    await signOut();
  };

  // Tap to view receipt
  const handleViewReceipt = (receiptId: number) => {
    navigation.navigate('ViewReceipt', { receiptId });
  };

  // Swipe or menu edit
  const handleEditReceipt = (receiptId: number) => {
    navigation.navigate('EditReceipt', { receiptId });
  };

  // Delete with confirmation (from swipe button tap)
  const handleDeleteWithConfirmation = (receiptId: number, supplier: string) => {
    Alert.alert(
      'Delete Receipt',
      `Are you sure you want to delete the receipt from "${supplier}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => performDelete(receiptId),
        },
      ]
    );
  };

  // Delete with undo (from long swipe)
  const handleDeleteWithUndo = (receiptId: number, supplier: string) => {
    setPendingDelete({ id: receiptId, supplier });
    setShowUndoSnackbar(true);
  };

  // Actually perform the delete
  const performDelete = async (receiptId: number) => {
    try {
      const { error } = await archiveReceipt(supabase as any, receiptId);
      if (error) {
        throw new Error(error.message);
      }
      await refresh();
    } catch (err) {
      Alert.alert('Error', err instanceof Error ? err.message : 'Failed to delete receipt');
    }
  };

  // Handle undo
  const handleUndo = () => {
    setPendingDelete(null);
    setShowUndoSnackbar(false);
    // Receipt was never actually deleted, just hidden from UI
  };

  // Handle snackbar dismiss (actually delete)
  const handleSnackbarDismiss = () => {
    if (pendingDelete) {
      performDelete(pendingDelete.id);
    }
    setPendingDelete(null);
    setShowUndoSnackbar(false);
  };

  // Long press to show context menu
  const handleLongPress = (receiptId: number, supplier: string) => {
    setSelectedReceipt({ id: receiptId, supplier });
    setShowContextMenu(true);
  };

  const handleAddReceipt = () => {
    navigation.navigate('AddReceipt');
  };

  // Context menu items
  const selectedReceiptStatus = selectedReceipt
    ? receipts.find(r => r.id === selectedReceipt.id)?.status
    : undefined;
  const allowModifySelected = canModifyReceipt(selectedReceiptStatus);

  const contextMenuItems: ContextMenuItem[] = selectedReceipt ? [
    {
      id: 'view',
      label: 'View Details',
      icon: 'eye',
      onPress: () => handleViewReceipt(selectedReceipt.id),
    },
    ...(allowModifySelected ? [{
      id: 'edit',
      label: 'Edit Receipt',
      icon: 'edit-2',
      onPress: () => handleEditReceipt(selectedReceipt.id),
    }] : []),
    ...(allowModifySelected ? [{
      id: 'delete',
      label: 'Delete Receipt',
      icon: 'trash-2',
      onPress: () => handleDeleteWithConfirmation(selectedReceipt.id, selectedReceipt.supplier),
      destructive: true,
    }] : []),
  ] : [];

  const renderEmpty = () => {
    if (loading) {
      return null;
    }

    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>No receipts found</Text>
        <Text style={styles.emptySubtext}>
          Tap the ADD button to create your first receipt
        </Text>
      </View>
    );
  };

  const renderFooter = () => {
    if (!hasMore) {
      return null;
    }

    return (
      <View style={styles.footerLoader}>
        <ActivityIndicator size="small" color="#00897B" />
      </View>
    );
  };

  // Filter out pending delete items from display
  const displayReceipts = pendingDelete 
    ? receipts.filter(r => r.id !== pendingDelete.id)
    : receipts;

  return (
    <GestureHandlerRootView style={styles.gestureRoot}>
      <SafeAreaView style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Receipts</Text>
          <TouchableOpacity onPress={handleSignOut} style={styles.profileButton}>
            <View style={styles.profileIcon}>
              <Text style={styles.profileIconText}>
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Add Button */}
        <TouchableOpacity style={styles.addButton} onPress={handleAddReceipt}>
          <Icon.Plus size={20} color="#fff" style={styles.addButtonIcon} />
          <Text style={styles.addButtonText}>Add Receipt</Text>
        </TouchableOpacity>

        {/* Error Message */}
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* Receipt List */}
        {loading && receipts.length === 0 ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#00897B" />
            <Text style={styles.loadingText}>Loading receipts...</Text>
          </View>
        ) : (
          <FlatList
            data={displayReceipts}
            keyExtractor={(item) => item.id.toString()}
            renderItem={({ item }) => (
              <SwipeableReceiptItem
                id={item.id}
                supplier={item.supplier || 'Unknown Supplier'}
                totalAmount={item.totalAmount}
                currency={item.currency}
                capturedDate={item.receipt_date || ''}
                status={item.status}
                onPress={() => handleViewReceipt(item.id)}
                onEdit={() => {
                  if (canModifyReceipt(item.status)) {
                    handleEditReceipt(item.id);
                  }
                }}
                onDelete={() => {
                  if (canModifyReceipt(item.status)) {
                    handleDeleteWithConfirmation(item.id, item.supplier || 'Unknown Supplier');
                  }
                }}
                onLongPress={() => handleLongPress(item.id, item.supplier || 'Unknown Supplier')}
              />
            )}
            ListEmptyComponent={renderEmpty}
            ListFooterComponent={renderFooter}
            refreshControl={
              <RefreshControl
                refreshing={false}
                onRefresh={refresh}
                colors={['#00897B']}
                tintColor="#00897B"
              />
            }
            onEndReached={loadMore}
            onEndReachedThreshold={0.5}
          />
        )}

        {/* Pagination Info */}
        {receipts.length > 0 && (
          <View style={styles.paginationInfo}>
            <Text style={styles.paginationText}>
              Showing {displayReceipts.length} receipt{displayReceipts.length !== 1 ? 's' : ''}
              {hasMore && ' • Pull down to refresh'}
            </Text>
          </View>
        )}

        {/* Context Menu */}
        <ContextMenu
          visible={showContextMenu}
          items={contextMenuItems}
          onClose={() => setShowContextMenu(false)}
          title={selectedReceipt?.supplier}
        />

        {/* Undo Snackbar */}
        <UndoSnackbar
          visible={showUndoSnackbar}
          message={`"${pendingDelete?.supplier}" deleted`}
          onUndo={handleUndo}
          onDismiss={handleSnackbarDismiss}
          duration={5000}
        />
      </SafeAreaView>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  gestureRoot: {
    flex: 1,
  },
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
  headerTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
  },
  profileButton: {
    padding: 4,
  },
  profileIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileIconText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#00897B',
  },
  addButton: {
    flexDirection: 'row',
    backgroundColor: '#00897B',
    padding: 16,
    margin: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  addButtonIcon: {
    marginRight: 4,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  errorContainer: {
    backgroundColor: '#FFEBEE',
    padding: 12,
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 8,
  },
  errorText: {
    color: '#C62828',
    fontSize: 14,
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
  emptyContainer: {
    padding: 48,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  footerLoader: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  paginationInfo: {
    padding: 12,
    backgroundColor: '#F5F5F5',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  paginationText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
});
