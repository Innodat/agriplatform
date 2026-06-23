import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Platform,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';

interface DatePickerFieldProps {
  value: string; // ISO date string (YYYY-MM-DD)
  onChange: (date: string) => void;
  label?: string;
  error?: string;
}

export function DatePickerField({
  value,
  onChange,
  label,
  error,
}: DatePickerFieldProps) {
  const [showPicker, setShowPicker] = useState(false);
  
  // Convert ISO string to Date object
  const dateValue = value ? new Date(value + 'T00:00:00') : new Date();

  const handleDateChange = (event: any, selectedDate?: Date) => {
    if (Platform.OS === 'android') {
      setShowPicker(false);
    }
    
    if (selectedDate) {
      // Convert to ISO date string (YYYY-MM-DD)
      const isoString = selectedDate.toISOString().split('T')[0];
      onChange(isoString);
    }
  };

  const formatDate = (dateString: string): string => {
    if (!dateString) return 'Select date';
    
    const date = new Date(dateString + 'T00:00:00');
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    
    return `${year}-${month}-${day}`;
  };

  return (
    <View style={styles.container}>
      {label && <Text style={styles.label}>{label}</Text>}
      
      <TouchableOpacity
        style={[styles.input, error && styles.inputError]}
        onPress={() => setShowPicker(true)}
      >
        <Text style={styles.inputText}>{formatDate(value)}</Text>
        <Text style={styles.calendarIcon}>📅</Text>
      </TouchableOpacity>

      {error && <Text style={styles.errorText}>{error}</Text>}

      {showPicker && (
        <DateTimePicker
          value={dateValue}
          mode="date"
          display={Platform.OS === 'ios' ? 'spinner' : 'default'}
          onChange={handleDateChange}
          maximumDate={new Date()}
        />
      )}

      {/* iOS requires a done button */}
      {showPicker && Platform.OS === 'ios' && (
        <View style={styles.iosButtonContainer}>
          <TouchableOpacity
            style={styles.iosDoneButton}
            onPress={() => setShowPicker(false)}
          >
            <Text style={styles.iosDoneButtonText}>Done</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 6,
  },
  input: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#fff',
  },
  inputError: {
    borderColor: '#C62828',
  },
  inputText: {
    fontSize: 16,
    color: '#333',
  },
  calendarIcon: {
    fontSize: 20,
  },
  errorText: {
    color: '#C62828',
    fontSize: 12,
    marginTop: 4,
  },
  iosButtonContainer: {
    alignItems: 'flex-end',
    marginTop: 8,
  },
  iosDoneButton: {
    backgroundColor: '#00897B',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  iosDoneButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
