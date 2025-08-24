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

    private static final String BASE_DIRECTORY = "/var/logs/app/";


    @GetMapping("/api/welcome")
    public WelcomeDTO welcome(@RequestParam(value = "name", defaultValue = "...") String name) {
        return new WelcomeDTO("Hola, bienvenido " +name + ", esto es un demo");
    }

     @GetMapping("/logs")
    public ResponseEntity<String> getLogFile(@RequestParam String filename) {
        try {
            
            Path filePath = Paths.get(BASE_DIRECTORY + filename);

            String content = new String(Files.readAllBytes(filePath));
            return ResponseEntity.ok(content);

        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Error: Archivo no encontrado.");
        }
    }


}