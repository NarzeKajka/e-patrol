import 'package:geocoding/geocoding.dart';
import 'package:geolocator/geolocator.dart';

class LocationResult {
  final double latitude;
  final double longitude;
  final String address;

  const LocationResult({
    required this.latitude,
    required this.longitude,
    required this.address,
  });
}

class LocationService {
  static final Geocoding _geocoding = Geocoding();

  static Future<LocationResult> getCurrentLocation() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();

    if (!serviceEnabled) {
      throw Exception(
        'Włącz usługi lokalizacyjne, aby użyć bieżącej lokalizacji.',
      );
    }

    LocationPermission permission = await Geolocator.checkPermission();

    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    if (permission == LocationPermission.denied) {
      throw Exception('Dostęp do lokalizacji nie został przyznany.');
    }

    if (permission == LocationPermission.deniedForever) {
      throw Exception(
        'Dostęp do lokalizacji został trwale wyłączony. '
        'Możesz go włączyć w ustawieniach urządzenia.',
      );
    }

    final position = await Geolocator.getCurrentPosition();

    final address = await getAddress(position.latitude, position.longitude);

    return LocationResult(
      latitude: position.latitude,
      longitude: position.longitude,
      address: address,
    );
  }

  static Future<String> getAddress(double latitude, double longitude) async {
    final placemarks = await _geocoding.placemarkFromCoordinates(
      latitude,
      longitude,
    );

    if (placemarks.isEmpty) {
      return 'Nieznana lokalizacja';
    }

    final place = placemarks.first;

    final addressParts = [
      place.street,
      place.postalCode,
      place.locality,
    ].where((part) => part != null && part.trim().isNotEmpty).toList();

    if (addressParts.isEmpty) {
      return 'Nieznana lokalizacja';
    }

    return addressParts.join(', ');
  }
}
