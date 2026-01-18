import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuth } from '../contexts/AuthContext';
import { LoginScreen } from '../screens/LoginScreen';
import { ForgotPasswordScreen } from '../screens/ForgotPasswordScreen';
import { ReceiptListScreen } from '../screens/ReceiptListScreen';
import { AddReceiptScreen } from '../screens/AddReceiptScreen';
import { EditReceiptScreen } from '../screens/EditReceiptScreen';
import { ActivityIndicator, View, StyleSheet } from 'react-native';

export type RootStackParamList = {
  // Auth Stack
  Login: undefined;
  ForgotPassword: undefined;
  
  // Main Stack
  ReceiptList: undefined;
  AddReceipt: undefined;
  EditReceipt: { receiptId: number };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export function RootNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#00897B" />
      </View>
    );
  }

  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      {!user ? (
        // Auth Stack
        <>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
        </>
      ) : (
        // Main Stack
        <>
          <Stack.Screen name="ReceiptList" component={ReceiptListScreen} />
          <Stack.Screen name="AddReceipt" component={AddReceiptScreen} />
          <Stack.Screen name="EditReceipt" component={EditReceiptScreen} />
        </>
      )}
    </Stack.Navigator>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
});
