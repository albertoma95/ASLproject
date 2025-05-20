import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart';

class HomePage extends StatefulWidget {
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  CameraController? _cameraController;
  bool _isCameraInitialized = false;
  String _status = "Esperando...";

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    final cameras = await availableCameras();
    final camera = cameras.first;

    _cameraController = CameraController(camera, ResolutionPreset.medium);

    await _cameraController!.initialize();
    setState(() => _isCameraInitialized = true);
  }

  Future<void> _captureImage() async {
    if (!_cameraController!.value.isInitialized) return;

    final directory = await getTemporaryDirectory();
    final path = join(directory.path, '${DateTime.now()}.png');

    try {
      final image = await _cameraController!.takePicture();
      final imageFile = File(image.path);
      setState(() {
        _status = "Imagen capturada: ${imageFile.path}";
      });

      // Aquí luego llamaremos al backend con esta imagen
    } catch (e) {
      setState(() => _status = "Error: $e");
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Captura de mano")),
      body: SafeArea(
        child: Column(
          children: [
            _isCameraInitialized
                ? Expanded(
                  child: AspectRatio(
                    aspectRatio: _cameraController!.value.aspectRatio,
                    child: CameraPreview(_cameraController!),
                  ),
                )
                : Expanded(child: Center(child: CircularProgressIndicator())),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _captureImage,
              child: Text("Capturar imagen"),
            ),
            SizedBox(height: 10),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Text(_status, textAlign: TextAlign.center),
            ),
          ],
        ),
      ),
    );
  }
}
