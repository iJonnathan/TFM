package com.demo.controllers;

import com.demo.models.WelcomeDTO;

import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class WelcomeController {
    // ❌ Vulnerabilidad 1: Reflected XSS (no sanitiza entrada del usuario)
    @GetMapping("/api/welcome")
    public WelcomeDTO welcome(@RequestParam(value = "name", defaultValue = "...") String name) {
        return new WelcomeDTO("Hola, bienvenido " + name + ", esto es un demo");
    }

    // ❌ Vulnerabilidad 2: Remote Code Execution (RCE) usando motor de scripting
    @PostMapping("/api/execute")
    public String executeCode(@RequestBody String userScript) throws Exception {
        ScriptEngineManager manager = new ScriptEngineManager();
        ScriptEngine engine = manager.getEngineByName("nashorn"); // obsoleto pero aún usado en ejemplos
        Object result = engine.eval(userScript); // ❌ Ejecuta lo que sea
        return "Resultado: " + result;
    }

    // ❌ Vulnerabilidad 3: Path Traversal (no valida ruta)
    @GetMapping("/api/read-file")
    public String readFile(@RequestParam String filePath) throws Exception {
        java.nio.file.Path path = java.nio.file.Paths.get(filePath); // ⚠ No sanitiza entrada
        return java.nio.file.Files.readString(path);
    }
}
