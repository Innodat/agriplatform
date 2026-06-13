import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Image,
  Alert,
  SafeAreaView,
  Dimensions,
} from 'react-native';
import ImageZoom from 'react-native-image-pan-zoom';

interface FullScreenImageViewerProps {
  visible: boolean;
  imageUri: string | null;
  onClose: () => void;
  onReplace: () => void;
  onDelete: () => void;
}

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

export function FullScreenImageViewer({
  visible,
  imageUri,
  onClose,
  onReplace,
  onDelete,
}: FullScreenImageViewerProps) {
  const [imageError, setImageError] = useState(false);

  const handleDelete = () => {
    Alert.alert(
      'Delete Image',
      'Are you sure you want to delete this receipt image?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            onDelete();
            onClose();
          },
        },
      ]
    );
  };

  const handleReplace = () => {
    onReplace();
    onClose();
  };

  return (
    <Modal
      visible={visible}
      transparent={false}
      animationType="fade"
      onRequestClose={onClose}
    >
      <SafeAreaView style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.headerButton}>
            <Text style={styles.headerButtonText}>✕</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Receipt Image</Text>
          <View style={styles.headerButton} />
        </View>

        {/* Image with Zoom/Pan */}
        <View style={styles.imageContainer}>
          {imageError ? (
            <View style={styles.errorContainer}>
              <Text style={styles.errorIcon}>⚠️</Text>
              <Text style={styles.errorText}>Failed to load image</Text>
              <TouchableOpacity style={styles.retryButton} onPress={() => setImageError(false)}>
                <Text style={styles.retryButtonText}>Retry</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <ImageZoom
              cropWidth={SCREEN_WIDTH}
              cropHeight={SCREEN_HEIGHT - 200}
              imageWidth={SCREEN_WIDTH}
              imageHeight={SCREEN_HEIGHT - 200}
              enableSwipeDown={true}
              onSwipeDown={onClose}
            >
              <Image
                source={{ uri: imageUri || '' }}
                style={styles.image}
                resizeMode="contain"
                onError={() => setImageError(true)}
              />
            </ImageZoom>
          )}
        </View>

        {/* Action Buttons */}
        <View style={styles.actions}>
          <TouchableOpacity style={styles.actionButton} onPress={handleReplace}>
            <Text style={styles.actionIcon}>🔄</Text>
            <Text style={styles.actionText}>Replace</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionButton, styles.deleteButton]} onPress={handleDelete}>
            <Text style={styles.actionIcon}>🗑️</Text>
            <Text style={[styles.actionText, styles.deleteText]}>Delete</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'rgba(0,0,0,0.8)',
  },
  headerButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerButtonText: {
    fontSize: 28,
    color: '#fff',
    fontWeight: '300',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
  },
  imageContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT - 200,
  },
  errorContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  errorIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  errorText: {
    fontSize: 18,
    color: '#fff',
    marginBottom: 24,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#00897B',
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  actions: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
    backgroundColor: 'rgba(0,0,0,0.8)',
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#333',
    padding: 16,
    borderRadius: 12,
    gap: 8,
  },
  deleteButton: {
    backgroundColor: '#C62828',
  },
  actionIcon: {
    fontSize: 20,
  },
  actionText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  deleteText: {
    color: '#fff',
  },
});
