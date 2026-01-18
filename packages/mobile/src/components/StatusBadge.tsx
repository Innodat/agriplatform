import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface StatusBadgeProps {
  status: 'pending' | 'approved' | 'rejected' | 'querying';
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const colors = {
    pending: { bg: '#E0E0E0', text: '#666' },
    approved: { bg: '#C8E6C9', text: '#2E7D32' },
    rejected: { bg: '#FFCDD2', text: '#C62828' },
    querying: { bg: '#FFE0B2', text: '#E65100' },
  };

  const labels = {
    pending: 'Pending',
    approved: 'Approved',
    rejected: 'Rejected',
    querying: 'Querying',
  };

  const { bg, text } = colors[status];

  return (
    <View style={[styles.badge, { backgroundColor: bg }]}>
      <Text style={[styles.badgeText, { color: text }]}>
        {labels[status]}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
});