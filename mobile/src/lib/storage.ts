import { Platform } from "react-native";
import * as SecureStore from "expo-secure-store";
const KEY = "kenfit.access-token";
// Web preview keeps the token in memory only; no persistence in browser storage.
let webToken: string | null = null;
export const readToken = () =>
  Platform.OS === "web"
    ? Promise.resolve(webToken)
    : SecureStore.getItemAsync(KEY);
export const saveToken = (value: string) =>
  Platform.OS === "web"
    ? Promise.resolve(void (webToken = value))
    : SecureStore.setItemAsync(KEY, value);
export const removeToken = () =>
  Platform.OS === "web"
    ? Promise.resolve(void (webToken = null))
    : SecureStore.deleteItemAsync(KEY);
