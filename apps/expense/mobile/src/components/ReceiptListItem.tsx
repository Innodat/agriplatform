import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { format, isToday } from 'date-fns';

interface ReceiptListItemProps {
  id: number;
  supplier: string;
  totalAmount: number;
  currency: string;
  capturedDate: string;
  onEdit: () => void;
}

export function ReceiptListItem({
  id,
  supplier,
  totalAmount,
  currency,
  capturedDate,
  onEdit,
}: ReceiptListItemProps) {
  const receiptDate = new Date(capturedDate);
  const isTodayReceipt = isToday(receiptDate);
  const formattedDate = format(receiptDate, 'dd/MM/yyyy');

  return (
    <View style={[styles.container, isTodayReceipt && styles.todayContainer]}>
      <View style={styles.content}>
        <Text style={styles.supplier} numberOfLines={1}>
          {supplier}
        </Text>
        <View style={styles.details}>
          <Text style={styles.amount}>
            {currency}
            {totalAmount.toFixed(2)}
          </Text>
          <Text style={styles.date}>{formattedDate}</Text>
        </View>
      </View>
      {isTodayReceipt && (
        <TouchableOpacity style={styles.editButton} onPress={onEdit}>
          <Text style={styles.editIcon}>✏️</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  todayContainer: {
    backgroundColor: '#E8F5E9',
  },
  content: {
    flex: 1,
  },
  supplier: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
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
    color: '#666',
  },
  editButton: {
    padding: 8,
    marginLeft: 8,
  },
  editIcon: {
    fontSize: 20,
  },
});
