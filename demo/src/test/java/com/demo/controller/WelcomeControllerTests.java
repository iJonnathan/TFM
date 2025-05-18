package com.demo.controller;

import com.demo.controllers.WelcomeController;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.hamcrest.Matchers.containsString; // Importación necesaria para containsString

@WebMvcTest(WelcomeController.class) // Anotación específica para probar controladores
public class WelcomeControllerTests {

	@Autowired // Inyecta la instancia de MockMvc para simular peticiones HTTP
	private MockMvc mockMvc;

	@Test // Marca este método como una prueba unitaria de JUnit 5
	public void welcomeEndpointReturnsDefaultMessage() throws Exception {
		mockMvc.perform(get("/api/welcome")) // Realiza una petición GET a /api/welcome
				.andExpect(status().isOk()) // Espera un estado HTTP 200 OK
				.andExpect(content().contentType("application/json")) // Espera que el contenido sea JSON
				.andExpect(jsonPath("$.message").value("Hola, bienvenido ..., esto es un demo")); // Verifica el valor del campo 'message' en el JSON
	}

	@Test // Otra prueba unitaria
	public void welcomeEndpointReturnsCustomMessage() throws Exception {
		mockMvc.perform(get("/api/welcome").param("name", "Juan")) // Petición GET con parámetro 'name'
				.andExpect(status().isOk())
				.andExpect(content().contentType("application/json"))
				.andExpect(jsonPath("$.message").value("Hola, Juan, esto es un demo")); // Verifica el mensaje con el nombre personalizado
	}
}