import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../theme/app_theme.dart';
import '../../../services/location_service.dart';
import '../../../widgets/app_button.dart';

class LocationPickerScreen extends StatefulWidget {
  final double? initialLatitude;
  final double? initialLongitude;

  const LocationPickerScreen({
    super.key,
    this.initialLatitude,
    this.initialLongitude,
  });

  @override
  State<LocationPickerScreen> createState() => _LocationPickerScreenState();
}

class _LocationPickerScreenState extends State<LocationPickerScreen> {
  static const LatLng _defaultCenter = LatLng(50.0647, 19.9450);

  late LatLng selectedPoint;

  String? selectedAddress;
  bool isLoadingAddress = false;

  @override
  void initState() {
    super.initState();

    selectedPoint =
        widget.initialLatitude != null && widget.initialLongitude != null
        ? LatLng(widget.initialLatitude!, widget.initialLongitude!)
        : _defaultCenter;

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _getAddress(selectedPoint);
    });
  }

  Future<void> _getAddress(LatLng point) async {
    setState(() {
      isLoadingAddress = true;
    });

    try {
      final address = await LocationService.getAddress(
        point.latitude,
        point.longitude,
      );

      if (!mounted) return;

      setState(() {
        selectedAddress = address;
        isLoadingAddress = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        selectedAddress = 'Nie udało się pobrać adresu';
        isLoadingAddress = false;
      });
    }
  }

  void _selectPoint(TapPosition tapPosition, LatLng point) {
    setState(() {
      selectedPoint = point;
      selectedAddress = null;
    });

    _getAddress(point);
  }

  void _confirmLocation() {
    Navigator.pop<Map<String, dynamic>>(context, {
      'latitude': selectedPoint.latitude,
      'longitude': selectedPoint.longitude,
      'address': selectedAddress,
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        title: const Text('Wybierz lokalizację'),
      ),
      body: Column(
        children: [
          Expanded(
            child: FlutterMap(
              options: MapOptions(
                initialCenter: selectedPoint,
                initialZoom: 15,
                onTap: _selectPoint,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.example.frontend',
                ),
                MarkerLayer(
                  markers: [
                    Marker(
                      point: selectedPoint,
                      width: 50,
                      height: 50,
                      child: const Icon(
                        Icons.location_pin,
                        size: 50,
                        color: AppTheme.primary,
                      ),
                    ),
                  ],
                ),
                const RichAttributionWidget(
                  attributions: [
                    TextSourceAttribution('OpenStreetMap contributors'),
                  ],
                ),
              ],
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 24),
            decoration: const BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Color(0x14000000),
                  blurRadius: 12,
                  offset: Offset(0, -3),
                ),
              ],
            ),
            child: SafeArea(
              top: false,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Wybrane miejsce',
                    style: TextStyle(fontSize: 13, color: Color(0xFF718096)),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Padding(
                        padding: EdgeInsets.only(top: 1),
                        child: Icon(
                          Icons.location_on_outlined,
                          color: AppTheme.primary,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: isLoadingAddress
                            ? const Text(
                                'Pobieranie adresu...',
                                style: TextStyle(
                                  fontSize: 15,
                                  color: Color(0xFF718096),
                                ),
                              )
                            : Text(
                                selectedAddress ?? 'Nieznana lokalizacja',
                                style: const TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w600,
                                  color: AppTheme.darkBlue,
                                ),
                              ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 18),
                  AppButton(
                    label: 'Zatwierdź lokalizację',
                    icon: Icons.check_rounded,
                    large: true,
                    onPressed: isLoadingAddress ? null : _confirmLocation,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
