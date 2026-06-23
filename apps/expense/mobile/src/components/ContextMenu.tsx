import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Pressable,
} from 'react-native';
import * as Icon from 'lucide-react-native';

export interface ContextMenuItem {
  id: string;
  label: string;
  icon: string;
  onPress: () => void;
  destructive?: boolean;
  disabled?: boolean;
}

interface ContextMenuProps {
  visible: boolean;
  items: ContextMenuItem[];
  onClose: () => void;
  title?: string;
}

export function ContextMenu({
  visible,
  items,
  onClose,
  title,
}: ContextMenuProps) {
  const handleItemPress = (item: ContextMenuItem) => {
    if (item.disabled) return;
    onClose();
    // Small delay to allow modal to close before action
    setTimeout(() => {
      item.onPress();
    }, 100);
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <Pressable style={styles.overlay} onPress={onClose}>
        <View style={styles.menuContainer}>
          {title && (
            <View style={styles.header}>
              <Text style={styles.title} numberOfLines={1}>
                {title}
              </Text>
            </View>
          )}
          {items.map((item, index) => (
            <TouchableOpacity
              key={item.id}
              style={[
                styles.menuItem,
                index === 0 && !title && styles.menuItemFirst,
                index === items.length - 1 && styles.menuItemLast,
                item.disabled && styles.menuItemDisabled,
              ]}
              onPress={() => handleItemPress(item)}
              activeOpacity={item.disabled ? 1 : 0.7}
            >
              {item.icon === 'eye' && (
                <Icon.Eye
                  size={20}
                  color={
                    item.disabled
                      ? '#9CA3AF'
                      : item.destructive
                      ? '#DC2626'
                      : '#374151'
                  }
                  style={styles.menuItemIcon}
                />
              )}
              {item.icon === 'edit-2' && (
                <Icon.Pencil
                  size={20}
                  color={
                    item.disabled
                      ? '#9CA3AF'
                      : item.destructive
                      ? '#DC2626'
                      : '#374151'
                  }
                  style={styles.menuItemIcon}
                />
              )}
              {item.icon === 'trash-2' && (
                <Icon.Trash2
                  size={20}
                  color={
                    item.disabled
                      ? '#9CA3AF'
                      : item.destructive
                      ? '#DC2626'
                      : '#374151'
                  }
                  style={styles.menuItemIcon}
                />
              )}
              <Text
                style={[
                  styles.menuItemText,
                  item.destructive && styles.menuItemTextDestructive,
                  item.disabled && styles.menuItemTextDisabled,
                ]}
              >
                {item.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  menuContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    width: '100%',
    maxWidth: 320,
    overflow: 'hidden',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    textAlign: 'center',
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  menuItemFirst: {
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  menuItemLast: {
    borderBottomWidth: 0,
    borderBottomLeftRadius: 12,
    borderBottomRightRadius: 12,
  },
  menuItemDisabled: {
    opacity: 0.5,
  },
  menuItemIcon: {
    marginRight: 12,
  },
  menuItemText: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500',
  },
  menuItemTextDestructive: {
    color: '#DC2626',
  },
  menuItemTextDisabled: {
    color: '#9CA3AF',
  },
});
