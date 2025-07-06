package com.demo.controllers;

import com.demo.models.WelcomeDTO;
import org.springframework.web.bind.annotation.*;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.sql.*;
import java.util.Base64;
import java.util.logging.Logger;

@RestController
public class WelcomeController {

    // ⚠ Logger mal usado con datos sensibles
    private static final Logger logger = Logger.getLogger(WelcomeController.class.getName());

    // ⚠ Hardcoded secret (clave embebida)
    private static final String DB_PASSWORD = "SuperSecreta123!";
    private static final String API_KEY = "ABC123-TOKEN-INSEGURO";

    // XSS
    @GetMapping("/api/welcome")
    public WelcomeDTO welcome(@RequestParam(value = "name", defaultValue = "...") String name) {
        return new WelcomeDTO("Hola, bienvenido " + name + ", esto es un demo");
    }

    // RCE
    @PostMapping("/api/execute")
    public String executeCode(@RequestBody String userScript) throws Exception {
        ScriptEngine engine = new ScriptEngineManager().getEngineByName("nashorn");
        return "Resultado: " + engine.eval(userScript);
    }

    // Path Traversal
    @GetMapping("/api/read-file")
    public String readFile(@RequestParam String filePath) throws Exception {
        return Files.readString(Paths.get(filePath));
    }

    // SQL Injection
    @GetMapping("/api/user")
    public String getUserInfo(@RequestParam String username) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/demo", "root", DB_PASSWORD);
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE username = '" + username + "'");
        if (rs.next()) {
            return "Usuario: " + rs.getString("username") + ", Email: " + rs.getString("email");
        }
        return "No encontrado";
    }

    // Command Injection
    @PostMapping("/api/ping")
    public String ping(@RequestBody String host) throws Exception {
        Process p = Runtime.getRuntime().exec("ping -c 1 " + host);
        BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) out.append(line).append("\n");
        return out.toString();
    }

    // Deserialización insegura
    @PostMapping("/api/deserialize")
    public String deserialize(@RequestBody String base64) throws Exception {
        byte[] data = Base64.getDecoder().decode(base64);
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
        Object obj = ois.readObject();
        return "Objeto: " + obj;
    }

    // Logs sensibles
    @PostMapping("/api/login")
    public String login(@RequestParam String user, @RequestParam String password) {
        logger.info("Intento de login con usuario: " + user + " y contraseña: " + password); // ⚠ Log inseguro
        return "Login procesado";
    }

    // Cifrado débil (uso de MD5)
    @GetMapping("/api/hash")
    public String hash(@RequestParam String data) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5"); // ⚠ Inseguro
        byte[] digest = md.digest(data.getBytes());
        return Base64.getEncoder().encodeToString(digest);
    }

    // Cifrado simétrico débil (AES con clave fija)
    @GetMapping("/api/encrypt")
    public String encrypt(@RequestParam String text) throws Exception {
        String key = "1234567890123456"; // ⚠ Clave estática
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes(), "AES");
        Cipher cipher = Cipher.getInstance("AES"); // sin GCM ni IV
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        return Base64.getEncoder().encodeToString(cipher.doFinal(text.getBytes()));
    }

    // Stacktrace expuesto
    @GetMapping("/api/error")
    public String error() {
        try {
            int a = 1 / 0;
            return "OK";
        } catch (Exception e) {
            return e.toString(); // ⚠ Devuelve detalles internos
        }
    }

    @GetMapping("/api/all-users-insecure")
    public String getAllUsersInsecure() throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/demo", "root", DB_PASSWORD);
        Statement stmt = conn.createStatement();
        // Una consulta que devuelve indiscriminadamente todos los registros de la tabla de usuarios.
        ResultSet rs = stmt.executeQuery("SELECT * FROM users");

        StringBuilder result = new StringBuilder("Todos los usuarios:\\n");
        while (rs.next()) {
            // Se asume que la tabla tiene columnas 'username', 'email' y 'password_hash'.
            // Exponer esta información es una brecha de seguridad masiva.
            result.append("Usuario: ").append(rs.getString("username"))
                  .append(", Email: ").append(rs.getString("email"))
                  .append(", PasswordData: ").append(rs.getString("password")) // Suponiendo que hay una columna de contraseña
                  .append("\\n");
        }
        return result.toString();
    }
}