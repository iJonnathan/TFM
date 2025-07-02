package com.demo.controllers;

import com.demo.models.WelcomeDTO;
import org.springframework.web.bind.annotation.*;

import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.*;
import java.util.Base64;
import java.io.ByteArrayInputStream;
import java.io.ObjectInputStream;

@RestController
public class WelcomeController {

    // ❌ Vulnerabilidad 1: Reflected XSS
    @GetMapping("/api/welcome")
    public WelcomeDTO welcome(@RequestParam(value = "name", defaultValue = "...") String name) {
        return new WelcomeDTO("Hola, bienvenido " + name + ", esto es un demo");
    }

    // ❌ Vulnerabilidad 2: Remote Code Execution
    @PostMapping("/api/execute")
    public String executeCode(@RequestBody String userScript) throws Exception {
        ScriptEngineManager manager = new ScriptEngineManager();
        ScriptEngine engine = manager.getEngineByName("nashorn");
        Object result = engine.eval(userScript);
        return "Resultado: " + result;
    }

    // ❌ Vulnerabilidad 3: Path Traversal
    @GetMapping("/api/read-file")
    public String readFile(@RequestParam String filePath) throws Exception {
        java.nio.file.Path path = Paths.get(filePath);
        return Files.readString(path);
    }

    // ❌ Vulnerabilidad 4: SQL Injection
    @GetMapping("/api/user")
    public String getUserInfo(@RequestParam String username) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/demo", "root", "password");
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE username = '" + username + "'");
        if (rs.next()) {
            return "Usuario: " + rs.getString("username") + ", Email: " + rs.getString("email");
        }
        return "Usuario no encontrado";
    }

    // ❌ Vulnerabilidad 5: Command Injection
    @PostMapping("/api/ping")
    public String ping(@RequestBody String host) throws Exception {
        Process p = Runtime.getRuntime().exec("ping -c 1 " + host);
        BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
        StringBuilder output = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            output.append(line).append("\n");
        }
        return output.toString();
    }

    // ❌ Vulnerabilidad 6: Deserialización insegura
    @PostMapping("/api/deserialize")
    public String deserialize(@RequestBody String base64) throws Exception {
        byte[] data = Base64.getDecoder().decode(base64);
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
        Object obj = ois.readObject();
        ois.close();
        return "Objeto deserializado: " + obj.toString();
    }

    // ❌ Vulnerabilidad 7: Falta de autenticación y headers inseguros
    @GetMapping("/api/headers")
    public String headers(@RequestHeader(value = "X-Token", required = false) String token) {
        // no se valida el token, ni se aplican controles de acceso
        return "Cabeceras recibidas. Token: " + token;
    }
}