import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Modal,
  SectionList,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';

interface PickerItem {
  id: number;
  name: string;
  symbol?: string;
  category?: string;
}

interface BottomSheetPickerProps {
  visible: boolean;
  title: string;
  items: PickerItem[];
  selectedId: number;
  onSelect: (id: number) => void;
  onClose: () => void;
  searchPlaceholder?: string;
  grouped?: boolean; // Whether to group items by category
}

interface SectionData {
  title: string;
  data: PickerItem[];
}

export function BottomSheetPicker({
  visible,
  title,
  items,
  selectedId,
  onSelect,
  onClose,
  searchPlaceholder = 'Search...',
  grouped = false,
}: BottomSheetPickerProps) {
  const [searchQuery, setSearchQuery] = useState('');

  // Group items by category if grouped is true
  const sections = useMemo((): SectionData[] => {
    const itemsToProcess = searchQuery.trim()
      ? items.filter(item =>
          item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.symbol?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.category?.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : items;

    if (!grouped) {
      // Return as single section without header
      return [{ title: '', data: itemsToProcess }];
    }

    // Group by category
    const groupedItems = itemsToProcess.reduce((acc, item) => {
      const category = item.category || 'Other';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(item);
      return acc;
    }, {} as Record<string, PickerItem[]>);

    // Convert to sections array and sort by category name
    return Object.entries(groupedItems)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([category, data]) => ({
        title: category,
        data,
      }));
  }, [items, searchQuery, grouped]);

  const handleSelect = (id: number) => {
    onSelect(id);
    setSearchQuery('');
    onClose();
  };

  const handleClose = () => {
    setSearchQuery('');
    onClose();
  };

  const renderItem = ({ item }: { item: PickerItem }) => (
    <TouchableOpacity
      style={styles.item}
      onPress={() => handleSelect(item.id)}
    >
      <Text style={styles.itemText}>
        {item.symbol ? `${item.symbol} ${item.name}` : item.name}
      </Text>
      {selectedId === item.id && (
        <Text style={styles.checkmark}>✓</Text>
      )}
    </TouchableOpacity>
  );

  const renderSectionHeader = ({ section }: { section: SectionData }) => {
    // Don't render header if title is empty (non-grouped mode)
    if (!section.title) {
      return null;
    }
    return (
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionHeaderText}>{section.title}</Text>
      </View>
    );
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={handleClose}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <TouchableOpacity
          style={styles.overlay}
          activeOpacity={1}
          onPress={handleClose}
        >
          <View style={styles.bottomSheet}>
            {/* Header */}
            <View style={styles.header}>
              <Text style={styles.title}>{title}</Text>
              <TouchableOpacity onPress={handleClose} style={styles.closeButton}>
                <Text style={styles.closeText}>✕</Text>
              </TouchableOpacity>
            </View>

            {/* Search Bar */}
            <View style={styles.searchContainer}>
              <Text style={styles.searchIcon}>🔍</Text>
              <TextInput
                style={styles.searchInput}
                placeholder={searchPlaceholder}
                value={searchQuery}
                onChangeText={setSearchQuery}
                autoCapitalize="none"
                autoCorrect={false}
              />
              {searchQuery.length > 0 && (
                <TouchableOpacity onPress={() => setSearchQuery('')}>
                  <Text style={styles.clearIcon}>✕</Text>
                </TouchableOpacity>
              )}
            </View>

            {/* List */}
            <SectionList
              sections={sections}
              keyExtractor={(item) => item.id.toString()}
              renderItem={renderItem}
              renderSectionHeader={renderSectionHeader}
              ListEmptyComponent={
                <View style={styles.emptyContainer}>
                  <Text style={styles.emptyText}>No items found</Text>
                </View>
              }
              style={styles.list}
              stickySectionHeadersEnabled={true}
            />
          </View>
        </TouchableOpacity>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  bottomSheet: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
    paddingBottom: Platform.OS === 'ios' ? 20 : 0,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  closeButton: {
    padding: 4,
  },
  closeText: {
    fontSize: 24,
    color: '#666',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    margin: 16,
    paddingHorizontal: 12,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  searchIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
    color: '#333',
  },
  clearIcon: {
    fontSize: 18,
    color: '#999',
    padding: 4,
  },
  list: {
    maxHeight: 400,
  },
  sectionHeader: {
    backgroundColor: '#F5F5F5',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  sectionHeaderText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    textTransform: 'uppercase',
  },
  item: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingLeft: 24,
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F5',
    backgroundColor: '#fff',
  },
  itemText: {
    fontSize: 16,
    color: '#333',
  },
  checkmark: {
    fontSize: 20,
    color: '#00897B',
    fontWeight: 'bold',
  },
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
});
