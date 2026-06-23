import React, { useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  Animated,
  Dimensions,
} from 'react-native';
import {
  Swipeable,
  GestureHandlerRootView,
} from 'react-native-gesture-handler';
import * as Icon from 'lucide-react-native';
import { format, isToday } from 'date-fns';
import { StatusBadge } from './StatusBadge';

const SCREEN_WIDTH = Dimensions.get('window').width;
const ACTION_WIDTH = 72;
const FULL_SWIPE_THRESHOLD = SCREEN_WIDTH * 0.6;

interface SwipeableReceiptItemProps {
  id: number;
  supplier: string;
  totalAmount: number;
  currency: string;
  capturedDate: string;
  status?: 'pending' | 'approved' | 'rejected' | 'querying';
  onPress: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onLongPress: () => void;
}

export function SwipeableReceiptItem({
  id,
  supplier,
  totalAmount,
  currency,
  capturedDate,
  status,
  onPress,
  onEdit,
  onDelete,
  onLongPress,
}: SwipeableReceiptItemProps) {
  const swipeableRef = useRef<Swipeable>(null);
  const receiptDate = new Date(capturedDate);
  const isTodayReceipt = isToday(receiptDate);
  const formattedDate = format(receiptDate, 'dd/MM/yyyy');

  const closeSwipeable = useCallback(() => {
    swipeableRef.current?.close();
  }, []);

  const handleEdit = useCallback(() => {
    closeSwipeable();
    onEdit();
  }, [closeSwipeable, onEdit]);

  const handleDelete = useCallback(() => {
    closeSwipeable();
    onDelete();
  }, [closeSwipeable, onDelete]);

  const canModify = status === 'pending' || status === 'querying';

  const renderRightActions = (
    progress: Animated.AnimatedInterpolation<number>,
    dragX: Animated.AnimatedInterpolation<number>
  ) => {
    if (!canModify) {
      return null;
    }
    // Edit button animation
    const editTranslateX = progress.interpolate({
      inputRange: [0, 0.5, 1],
      outputRange: [ACTION_WIDTH * 2, ACTION_WIDTH, 0],
    });

    // Delete button animation
    const deleteTranslateX = progress.interpolate({
      inputRange: [0, 0.5, 1],
      outputRange: [ACTION_WIDTH, ACTION_WIDTH / 2, 0],
    });

    // Scale for full swipe
    const scale = dragX.interpolate({
      inputRange: [-FULL_SWIPE_THRESHOLD, -ACTION_WIDTH * 2],
      outputRange: [1.2, 1],
      extrapolate: 'clamp',
    });

    return (
      <View style={styles.rightActionsContainer}>
        {/* Edit Button */}
        <Animated.View
          style={[
            styles.actionButton,
            styles.editAction,
            { transform: [{ translateX: editTranslateX }] },
          ]}
        >
          <Pressable
            style={styles.actionPressable}
            onPress={handleEdit}
            android_ripple={{ color: 'rgba(255,255,255,0.3)' }}
          >
            <Icon.Pencil size={22} color="#fff" />
            <Text style={styles.actionText}>Edit</Text>
          </Pressable>
        </Animated.View>

        {/* Delete Button */}
        <Animated.View
          style={[
            styles.actionButton,
            styles.deleteAction,
            { transform: [{ translateX: deleteTranslateX }, { scale }] },
          ]}
        >
          <Pressable
            style={styles.actionPressable}
            onPress={handleDelete}
            android_ripple={{ color: 'rgba(255,255,255,0.3)' }}
          >
            <Icon.Trash2 size={22} color="#fff" />
            <Text style={styles.actionText}>Delete</Text>
          </Pressable>
        </Animated.View>
      </View>
    );
  };

  const handleSwipeableOpen = (direction: 'left' | 'right') => {
    // If fully swiped, trigger delete with undo
    // This is handled by onSwipeableWillOpen with threshold check
  };

  const handleSwipeableWillOpen = (direction: 'left' | 'right') => {
    // Check if it's a full swipe (long swipe)
    // The Swipeable component handles this internally
  };

  return (
    <Swipeable
      ref={swipeableRef}
      renderRightActions={renderRightActions}
      rightThreshold={ACTION_WIDTH}
      overshootRight={false}
      friction={2}
      onSwipeableOpen={handleSwipeableOpen}
    >
      <Pressable
        style={[styles.container, isTodayReceipt && styles.todayContainer]}
        onPress={onPress}
        onLongPress={onLongPress}
        delayLongPress={500}
        android_ripple={{ color: 'rgba(0,0,0,0.1)' }}
      >
        <View style={styles.content}>
          <View style={styles.mainInfo}>
            <Text style={styles.supplier} numberOfLines={1}>
              {supplier}
            </Text>
            {isTodayReceipt && (
              <View style={styles.todayBadge}>
                <Text style={styles.todayBadgeText}>Today</Text>
              </View>
            )}
          </View>
          {status && (
            <View style={styles.statusContainer}>
              <StatusBadge status={status} />
            </View>
          )}
          <View style={styles.details}>
            <Text style={styles.amount}>
              {currency}
              {totalAmount.toFixed(2)}
            </Text>
            <Text style={styles.date}>{formattedDate}</Text>
          </View>
        </View>
        <View style={styles.chevronContainer}>
          <Icon.ChevronRight size={20} color="#9CA3AF" />
        </View>
      </Pressable>
    </Swipeable>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  todayContainer: {
    backgroundColor: '#ECFDF5',
  },
  content: {
    flex: 1,
  },
  mainInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  statusContainer: {
    marginBottom: 6,
  },
  supplier: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    flex: 1,
  },
  todayBadge: {
    backgroundColor: '#10B981',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    marginLeft: 8,
  },
  todayBadgeText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#fff',
  },
  details: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  amount: {
    fontSize: 14,
    fontWeight: '500',
    color: '#00897B',
  },
  date: {
    fontSize: 14,
    color: '#6B7280',
  },
  chevronContainer: {
    marginLeft: 8,
  },
  rightActionsContainer: {
    flexDirection: 'row',
    alignItems: 'stretch',
  },
  actionButton: {
    width: ACTION_WIDTH,
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionPressable: {
    flex: 1,
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 8,
  },
  editAction: {
    backgroundColor: '#00897B',
  },
  deleteAction: {
    backgroundColor: '#DC2626',
  },
  actionText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginTop: 4,
  },
});
