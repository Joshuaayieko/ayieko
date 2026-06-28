/// App-wide configuration.
///
/// Override the API base URL at build/run time with:
///   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
///
/// Note: 10.0.2.2 is the Android emulator's alias for the host machine's
/// localhost. On a physical device use your machine's LAN IP.
class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static const String appName = 'Orbes';
}
