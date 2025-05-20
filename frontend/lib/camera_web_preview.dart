import 'dart:async';
import 'dart:html' as html;
import 'dart:ui' as ui;
import 'package:flutter/material.dart';

class WebCameraPage extends StatefulWidget {
  @override
  _WebCameraPageState createState() => _WebCameraPageState();
}

class _WebCameraPageState extends State<WebCameraPage> {
  late html.VideoElement _videoElement;
  Timer? _timer;
  String _responseText = '';
  bool _sending = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  void _initializeCamera() async {
    _videoElement =
        html.VideoElement()
          ..width = 640
          ..height = 480
          ..autoplay = true;

    // Registrar vista para Flutter Web
    // ignore: undefined_prefixed_name
    ui.platformViewRegistry.registerViewFactory(
      'webcamVideoElement',
      (int viewId) => _videoElement,
    );

    try {
      final stream = await html.window.navigator.mediaDevices?.getUserMedia({
        'video': {'facingMode': 'user'},
      });
      _videoElement.srcObject = stream;
    } catch (e) {
      print('Error al acceder a la cámara: $e');
    }
  }

  void _startStreaming() {
    if (_sending) return;
    _sending = true;

    _timer = Timer.periodic(Duration(milliseconds: 250), (timer) async {
      await _captureAndSend();
    });
  }

  void _stopStreaming() {
    _timer?.cancel();
    _sending = false;
  }

  Future<void> _captureAndSend() async {
    final canvas = html.CanvasElement(width: 640, height: 480);
    final ctx = canvas.context2D;
    ctx.drawImage(_videoElement, 0, 0);

    final blob = await canvas.toBlob('image/png');

    if (blob == null) {
      print("No se pudo capturar la imagen.");
      return;
    }

    final formData = html.FormData();
    formData.appendBlob('file', blob, 'capture.png');

    final request = html.HttpRequest();

    request.open('POST', 'http://localhost:8000/upload/');

    request.onLoad.listen((event) {
      if (request.status == 200) {
        setState(() {
          _responseText = 'Respuesta backend: ${request.responseText}';
        });
      } else {
        setState(() {
          _responseText = 'Error en la subida: ${request.status}';
        });
      }
    });

    request.onError.listen((event) {
      setState(() {
        _responseText = 'Error en la conexión';
      });
    });

    request.send(formData);
  }

  @override
  void dispose() {
    _stopStreaming();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Streaming cámara (Web)")),
      body: Center(
        child: Column(
          children: [
            const SizedBox(height: 20),
            SizedBox(
              width: 640,
              height: 480,
              child: HtmlElementView(viewType: 'webcamVideoElement'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _sending ? _stopStreaming : _startStreaming,
              child: Text(_sending ? "Detener streaming" : "Iniciar streaming"),
            ),
            const SizedBox(height: 20),
            Text(_responseText),
          ],
        ),
      ),
    );
  }
}
