import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:http_parser/http_parser.dart';

import '../models/analysis_result.dart';

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000';

  static Future<String> login({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return data['access_token'];
    }

    throw Exception(data['detail'] ?? 'Nie udało się zalogować');
  }

  static Future<void> register({
    required String full_name,
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'full_name': full_name,
        'email': email,
        'password': password,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 201) {
      return;
    }

    throw Exception(data['detail'] ?? 'Nie udało się utworzyć konta');
  }

  static Future<Map<String, dynamic>> getMe({required String token}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/users/me'),
      headers: {'Authorization': 'Bearer $token'},
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return data;
    }

    throw Exception(
      data['detail'] ?? 'Nie udało się pobrać danych użytkownika',
    );
  }

  static Future<List<dynamic>> getMyReports({required String token}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/reports/my'),
      headers: {'Authorization': 'Bearer $token'},
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return data as List<dynamic>;
    }

    throw Exception(data['detail'] ?? 'Nie udało się pobrać zgłoszeń');
  }

  static Future<Map<String, dynamic>> createReport({
    required String token,
    required String category,
    required String? description,
    required double latitude,
    required double longitude,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/reports'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'category': category,
        'description': description,
        'latitude': latitude,
        'longitude': longitude,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 201) {
      return data as Map<String, dynamic>;
    }

    throw Exception(data['detail'] ?? 'Nie udało się utworzyć zgłoszenia');
  }

  static Future<Map<String, dynamic>> uploadReportImage({
    required String token,
    required int reportId,
    required XFile image,
  }) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/reports/$reportId/images'),
    );

    request.headers['Authorization'] = 'Bearer $token';

    final extension = image.name.split('.').last.toLowerCase();

    final MediaType contentType;

    switch (extension) {
      case 'png':
        contentType = MediaType('image', 'png');
        break;
      case 'heic':
        contentType = MediaType('image', 'heic');
        break;
      case 'heif':
        contentType = MediaType('image', 'heif');
        break;
      default:
        contentType = MediaType('image', 'jpeg');
    }

    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        image.path,
        filename: image.name,
        contentType: contentType,
      ),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    final data = jsonDecode(response.body);

    if (response.statusCode == 201) {
      return data as Map<String, dynamic>;
    }

    throw Exception(data['detail'] ?? 'Nie udało się przesłać zdjęcia');
  }

  static Future<Map<String, dynamic>> createAnalysis({
    required String token,
    required int imageId,
    required AnalysisResult analysis,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/images/$imageId/analyses'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(analysis.toJson()),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 201) {
      return data as Map<String, dynamic>;
    }

    throw Exception(data['detail'] ?? 'Nie udało się zapisać analizy');
  }

  static Future<Map<String, dynamic>> getReport({
    required String token,
    required int reportId,
  }) async {
    final response = await http.get(
      Uri.parse('$baseUrl/reports/$reportId'),
      headers: {'Authorization': 'Bearer $token'},
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return data as Map<String, dynamic>;
    }

    throw Exception(data['detail'] ?? 'Nie udało się pobrać zgłoszenia');
  }
}
