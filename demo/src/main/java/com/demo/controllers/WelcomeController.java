package com.demo.controllers;
import com.demo.models.WelcomeDTO;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Base64;
import java.util.logging.Level;
import java.util.logging.Logger;

@RestController
public class WelcomeController {

    private static final Logger logger = Logger.getLogger(WelcomeController.class.getName());
    private static final int GCM_TAG_LENGTH = 128;

    // SOLUCIÓN (Hardcoded Secrets): Inyecta secretos desde propiedades o variables de entorno.
    @Value("${app.db.password:default_db_password}")
    private String dbPassword;

    @Value("${app.secret.key:default_encryption_key_12345678}")
    private String encryptionKey;

    // SOLUCIÓN (XSS): Se codifica la entrada del usuario para neutralizar scripts.
    @GetMapping("/api/welcome")
    public WelcomeDTO welcome(@RequestParam(value = "name", defaultValue = "...") String name) {
        return new WelcomeDTO("Hola, bienvenido " +name + ", esto es un demo");
    }
    
    // SOLUCIÓN (Path Traversal): Se valida que la ruta no salga de un directorio base.
    @GetMapping("/api/read-file")
    public String readFile(@RequestParam String filePath) throws IOException {
        Path safeBaseDir = Paths.get("/tmp/safe-content/").toAbsolutePath();
        Path requestedPath = safeBaseDir.resolve(filePath).normalize();

        if (!requestedPath.startsWith(safeBaseDir)) {
            throw new SecurityException("Acceso a ruta de archivo no permitido.");
        }
        return "Acceso a archivo seguro verificado para: " + requestedPath;
    }

    // SOLUCIÓN (SQL Injection): Se usa PreparedStatement para evitar la inyección de SQL.
    @GetMapping("/api/user")
    public String getUserInfo(@RequestParam String username) throws Exception {
        String query = "SELECT * FROM users WHERE username = ?";
        try (Connection conn = DriverManager.getConnection("jdbc:h2:mem:testdb", "sa", "");
             PreparedStatement stmt = conn.prepareStatement(query)) {

            stmt.setString(1, username);
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    return "Usuario: " + rs.getString("username") + ", Email: " + rs.getString("email");
                }
            }
        }
        return "Usuario no encontrado";
    }

    // SOLUCIÓN (Logs sensibles): Se elimina la contraseña del mensaje de log.
    @PostMapping("/api/login")
    public String login(@RequestParam String user, @RequestParam String password) {
        logger.info("Intento de login para el usuario: " + user);
        return "Login procesado para el usuario: " + user;
    }

    // SOLUCIÓN (Cifrado débil): Se reemplaza MD5 por un algoritmo fuerte como SHA-256.
    @GetMapping("/api/hash")
    public String hash(@RequestParam String data) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] digest = md.digest(data.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(digest);
    }
    

    // SOLUCIÓN (Cifrado simétrico débil): Se usa un modo seguro (GCM) y un Vector de Inicialización (IV) aleatorio.
    @GetMapping("/api/encrypt")
    public String encrypt(@RequestParam String text) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        byte[] iv = new byte[cipher.getBlockSize()];
        new SecureRandom().nextBytes(iv);
        GCMParameterSpec parameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH, iv);

        cipher.init(Cipher.ENCRYPT_MODE, null, parameterSpec);
        byte[] cipherText = cipher.doFinal(text.getBytes(StandardCharsets.UTF_8));
        
        ByteBuffer byteBuffer = ByteBuffer.allocate(iv.length + cipherText.length);
        byteBuffer.put(iv);
        byteBuffer.put(cipherText);
        return Base64.getEncoder().encodeToString(byteBuffer.array());
    }

    // SOLUCIÓN (Stacktrace expuesto): La excepción será manejada por el método de abajo.
    @GetMapping("/api/error")
    public void error() {
        throw new IllegalStateException("Error de prueba para el manejador de excepciones local.");
    }
    
    // --- MANEJADOR DE EXCEPCIONES LOCAL ---
    // SOLUCIÓN (Stacktrace expuesto): Este método intercepta excepciones de este controlador,
    // las registra en el log y devuelve un mensaje genérico al cliente.
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public String handleControllerException(Exception ex) {
        logger.log(Level.SEVERE, "Error en WelcomeController: " + ex.getMessage(), ex);
        return "Ocurrió un error interno en el servidor.";
    }


}