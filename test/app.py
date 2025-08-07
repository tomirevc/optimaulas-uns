from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import random
import json
import io
import os
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
CORS(app)

class AulaOptimizer:
    def __init__(self):
        self.cursos = []
        self.aulas = []
        self.horarios = []
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        
    def load_data(self, cursos_file, aulas_file):
        """Cargar datos desde archivos Excel"""
        try:
            # Cargar cursos
            cursos_df = pd.read_excel(cursos_file)
            self.cursos = cursos_df.to_dict('records')
            
            # Cargar aulas
            aulas_df = pd.read_excel(aulas_file)
            self.aulas = aulas_df.to_dict('records')
            
            return True, "Datos cargados correctamente"
        except Exception as e:
            return False, f"Error al cargar datos: {str(e)}"
    
    def validate_assignment(self, assignment):
        """Validar que una asignación no tenga conflictos"""
        conflicts = 0
        aula_schedule = {}
        
        for curso_id, aula_id, horario in assignment:
            curso = next(c for c in self.cursos if c['id'] == curso_id)
            aula = next(a for a in self.aulas if a['id'] == aula_id)
            
            # Verificar capacidad
            if curso['tipo'] == 'teoria' and curso['estudiantes'] > aula['capacidad']:
                conflicts += 1
            elif curso['tipo'] == 'laboratorio' and curso['estudiantes'] > 15:
                conflicts += 1
            
            # Verificar disponibilidad de horario
            key = f"{aula_id}_{horario}"
            if key in aula_schedule:
                conflicts += 1
            else:
                aula_schedule[key] = curso_id
                
        return conflicts
    
    def fitness_function(self, individual):
        """Función de aptitud para evaluar una solución"""
        conflicts = self.validate_assignment(individual)
        distance_penalty = 0
        
        # Penalizar uso de aulas externas
        for curso_id, aula_id, horario in individual:
            aula = next(a for a in self.aulas if a['id'] == aula_id)
            if aula.get('tipo') == 'externa':
                distance_penalty += aula.get('distancia', 0) * 0.1
        
        # Mayor fitness = mejor solución (minimizar conflictos y distancia)
        fitness = 1000 - (conflicts * 100) - distance_penalty
        return max(fitness, 0)
    
    def create_individual(self):
        """Crear un individuo (solución) aleatorio"""
        individual = []
        for curso in self.cursos:
            # Seleccionar aula compatible
            compatible_aulas = [a for a in self.aulas 
                              if (curso['tipo'] == 'teoria' and a['tipo'] in ['teoria', 'externa']) or
                                 (curso['tipo'] == 'laboratorio' and a['tipo'] == 'laboratorio')]
            
            if compatible_aulas:
                aula = random.choice(compatible_aulas)
                # Generar horario aleatorio
                horario = self.generate_random_schedule(curso['duracion'])
                individual.append((curso['id'], aula['id'], horario))
        
        return individual
    
    def generate_random_schedule(self, duracion):
        """Generar horario aleatorio válido"""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        dia = random.choice(dias)
        
        # Horarios disponibles: 7-13 y 14-21
        morning_slots = [(7, 9), (9, 11), (11, 13)]
        afternoon_slots = [(14, 16), (16, 18), (18, 20), (19, 21)]
        
        if duracion == 2:
            slot = random.choice(morning_slots + afternoon_slots)
            return f"{dia} {slot[0]:02d}:00-{slot[1]:02d}:00"
        else:  # duracion == 4
            if random.choice([True, False]):
                return f"{dia} 07:00-11:00"
            else:
                return f"{dia} 14:00-18:00"
    
    def crossover(self, parent1, parent2):
        """Operador de cruzamiento"""
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        
        return child1, child2
    
    def mutate(self, individual):
        """Operador de mutación"""
        if random.random() > self.mutation_rate:
            return individual
        
        # Mutar un gen aleatorio
        idx = random.randint(0, len(individual) - 1)
        curso_id, _, _ = individual[idx]
        curso = next(c for c in self.cursos if c['id'] == curso_id)
        
        # Seleccionar nueva aula
        compatible_aulas = [a for a in self.aulas 
                          if (curso['tipo'] == 'teoria' and a['tipo'] in ['teoria', 'externa']) or
                             (curso['tipo'] == 'laboratorio' and a['tipo'] == 'laboratorio')]
        
        if compatible_aulas:
            new_aula = random.choice(compatible_aulas)
            new_schedule = self.generate_random_schedule(curso['duracion'])
            individual[idx] = (curso_id, new_aula['id'], new_schedule)
        
        return individual
    
    def genetic_algorithm(self):
        """Algoritmo genético principal"""
        # Inicializar población
        population = [self.create_individual() for _ in range(self.population_size)]
        
        best_fitness_history = []
        
        for generation in range(self.generations):
            # Evaluar fitness
            fitness_scores = [self.fitness_function(individual) for individual in population]
            
            # Registrar mejor fitness
            best_fitness = max(fitness_scores)
            best_fitness_history.append(best_fitness)
            
            # Selección por torneo
            new_population = []
            for _ in range(self.population_size // 2):
                # Seleccionar padres
                parent1 = self.tournament_selection(population, fitness_scores)
                parent2 = self.tournament_selection(population, fitness_scores)
                
                # Cruzamiento
                child1, child2 = self.crossover(parent1, parent2)
                
                # Mutación
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population
        
        # Retornar mejor solución
        final_fitness = [self.fitness_function(individual) for individual in population]
        best_idx = final_fitness.index(max(final_fitness))
        
        return population[best_idx], best_fitness_history
    
    def tournament_selection(self, population, fitness_scores, tournament_size=3):
        """Selección por torneo"""
        selected_indices = random.sample(range(len(population)), tournament_size)
        best_idx = max(selected_indices, key=lambda i: fitness_scores[i])
        return population[best_idx]
    
    def format_solution(self, solution):
        """Formatear solución para presentación"""
        formatted_solution = []
        for curso_id, aula_id, horario in solution:
            curso = next(c for c in self.cursos if c['id'] == curso_id)
            aula = next(a for a in self.aulas if a['id'] == aula_id)
            
            formatted_solution.append({
                'curso_id': curso_id,
                'curso_nombre': curso.get('nombre', f'Curso {curso_id}'),
                'ciclo': curso.get('ciclo', 'N/A'),
                'tipo': curso.get('tipo', 'teoria'),
                'estudiantes': curso.get('estudiantes', 0),
                'duracion': curso.get('duracion', 2),
                'aula_id': aula_id,
                'aula_nombre': aula.get('nombre', f'Aula {aula_id}'),
                'aula_tipo': aula.get('tipo', 'teoria'),
                'capacidad': aula.get('capacidad', 0),
                'ubicacion': aula.get('ubicacion', 'Campus'),
                'horario': horario
            })
        
        return formatted_solution

# Instancia global del optimizador
optimizer = AulaOptimizer()

@app.route('/')
def index():
    return jsonify({"message": "API de Optimización de Aulas - UNS"})

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'cursos' not in request.files or 'aulas' not in request.files:
            return jsonify({"error": "Faltan archivos requeridos"}), 400
        
        cursos_file = request.files['cursos']
        aulas_file = request.files['aulas']
        
        # Guardar archivos temporalmente
        cursos_path = f"temp_cursos_{uuid.uuid4()}.xlsx"
        aulas_path = f"temp_aulas_{uuid.uuid4()}.xlsx"
        
        cursos_file.save(cursos_path)
        aulas_file.save(aulas_path)
        
        # Cargar datos
        success, message = optimizer.load_data(cursos_path, aulas_path)
        
        # Limpiar archivos temporales
        os.remove(cursos_path)
        os.remove(aulas_path)
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "stats": {
                    "cursos": len(optimizer.cursos),
                    "aulas": len(optimizer.aulas)
                }
            })
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": f"Error procesando archivos: {str(e)}"}), 500

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        if not optimizer.cursos or not optimizer.aulas:
            return jsonify({"error": "No hay datos cargados"}), 400
        
        # Ejecutar algoritmo genético
        best_solution, fitness_history = optimizer.genetic_algorithm()
        
        # Formatear resultado
        formatted_solution = optimizer.format_solution(best_solution)
        
        # Calcular estadísticas
        conflicts = optimizer.validate_assignment(best_solution)
        
        return jsonify({
            "success": True,
            "solution": formatted_solution,
            "statistics": {
                "total_assignments": len(formatted_solution),
                "conflicts": conflicts,
                "fitness_history": fitness_history,
                "best_fitness": max(fitness_history),
                "generations": len(fitness_history)
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Error en optimización: {str(e)}"}), 500

@app.route('/download_result', methods=['POST'])
def download_result():
    try:
        data = request.json
        solution = data.get('solution', [])
        
        # Crear DataFrame
        df = pd.DataFrame(solution)
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Asignacion_Aulas', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'asignacion_aulas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        return jsonify({"error": f"Error generando descarga: {str(e)}"}), 500

@app.route('/download_templates', methods=['GET'])
def download_templates():
    try:
        # Crear templates de ejemplo
        cursos_template = pd.DataFrame({
            'id': [1, 2, 3, 4],
            'nombre': ['Algoritmos I', 'Base de Datos', 'Lab Algoritmos I', 'Lab Base de Datos'],
            'ciclo': [3, 4, 3, 4],
            'tipo': ['teoria', 'teoria', 'laboratorio', 'laboratorio'],
            'estudiantes': [40, 35, 15, 15],
            'duracion': [2, 2, 2, 2]
        })
        
        aulas_template = pd.DataFrame({
            'id': ['A101', 'A102', 'LAB01', 'LAB02', 'EXT01'],
            'nombre': ['Aula 101', 'Aula 102', 'Laboratorio 1', 'Laboratorio 2', 'Aula Externa 1'],
            'tipo': ['teoria', 'teoria', 'laboratorio', 'laboratorio', 'externa'],
            'capacidad': [45, 45, 15, 15, 50],
            'ubicacion': ['Campus', 'Campus', 'Campus', 'Campus', 'Pool de Aulas'],
            'distancia': [0, 0, 0, 0, 5]
        })
        
        # Crear archivo Excel con múltiples hojas
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            cursos_template.to_excel(writer, sheet_name='Cursos', index=False)
            aulas_template.to_excel(writer, sheet_name='Aulas', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='templates_asignacion_aulas.xlsx'
        )
        
    except Exception as e:
        return jsonify({"error": f"Error generando templates: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))