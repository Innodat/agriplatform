import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Platform,
} from 'react-native';

interface ImagePickerBottomSheetProps {
  visible: boolean;
  onClose: () => void;
  onTakePhoto: () => void;
  onChooseFromGallery: () => void;
}

export function ImagePickerBottomSheet({
  visible,
  onClose,
  onTakePhoto,
  onChooseFromGallery,
}: ImagePickerBottomSheetProps) {
  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <TouchableOpacity
        style={styles.overlay}
        activeOpacity={1}
        onPress={onClose}
      >
        <View style={styles.bottomSheet}>
          <View style={styles.handle} />
          
          <Text style={styles.title}>Add Receipt Image</Text>
          
          <TouchableOpacity
            style={styles.option}
            onPress={() => {
              onTakePhoto();
              onClose();
            }}
          >
            <View style={styles.iconContainer}>
              <Text style={styles.icon}>📷</Text>
            </View>
            <View style={styles.optionTextContainer}>
              <Text style={styles.optionTitle}>Take Photo</Text>
              <Text style={styles.optionSubtitle}>Use camera to capture receipt</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.option}
            onPress={() => {
              onChooseFromGallery();
              onClose();
            }}
          >
            <View style={styles.iconContainer}>
              <Text style={styles.icon}>🖼️</Text>
            </View>
            <View style={styles.optionTextContainer}>
              <Text style={styles.optionTitle}>Choose from Gallery</Text>
              <Text style={styles.optionSubtitle}>Select from your photos</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.cancelButton}
            onPress={onClose}
          >
            <Text style={styles.cancelText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  bottomSheet: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingBottom: Platform.OS === 'ios' ? 34 : 24,
    paddingTop: 8,
  },
  handle: {
    width: 40,
    height: 4,
    backgroundColor: '#E0E0E0',
    borderRadius: 2,
    alignSelf: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
    marginBottom: 24,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 8,
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  icon: {
    fontSize: 24,
  },
  optionTextContainer: {
    flex: 1,
  },
  optionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  optionSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  cancelButton: {
    marginTop: 8,
    marginHorizontal: 16,
    padding: 16,
    alignItems: 'center',
  },
  cancelText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
  },
});
