import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  FlatList,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useReceipts } from '../hooks/useReceipts';
import { ReceiptListItem } from '../components/ReceiptListItem';

export function ReceiptListScreen({ navigation }: any) {
  const { user, signOut } = useAuth();
  const { receipts, loading, error, refresh, loadMore, hasMore } = useReceipts();

  const handleSignOut = async () => {
    await signOut();
  };

  const handleEditReceipt = (receiptId: number) => {
    // TODO: Implement edit screen
    console.log('Edit receipt:', receiptId);
  };

  const handleAddReceipt = () => {
    navigation.navigate('AddReceipt');
  };

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

  return (
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
        <Text style={styles.addButtonText}>ADD</Text>
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
          data={receipts}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <ReceiptListItem
              id={item.id}
              supplier={item.supplier || 'Unknown Supplier'}
              totalAmount={item.totalAmount}
              currency={item.currency}
              capturedDate={item.created_timestamp || item.created_at || ''}
              onEdit={() => handleEditReceipt(item.id)}
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
            Showing {receipts.length} receipt{receipts.length !== 1 ? 's' : ''}
            {hasMore && ' • Pull down to refresh'}
          </Text>
        </View>
      )}
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
    backgroundColor: '#00897B',
    padding: 16,
    margin: 16,
    borderRadius: 8,
    alignItems: 'center',
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
