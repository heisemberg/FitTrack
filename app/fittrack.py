from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from app.auth import login_required
from app.db import get_db

bp = Blueprint('fittrack', __name__)

def calcular_macros(peso, genero, objetivo, porcentaje):
    if genero == 'M':
        cal = peso * 35
    elif genero == 'F':
        cal = peso * 33
    else:
        raise ValueError("Género inválido")

    if objetivo == 'mantener':
        cal_objetivo = cal
    elif objetivo == 'subir':
        cal_objetivo = cal + cal * porcentaje / 100
    elif objetivo == 'bajar':
        cal_objetivo = cal - cal * porcentaje / 100
    else:
        raise ValueError("Objetivo inválido")

    prot = 2 * peso  # Ejemplo de gramos de proteína por kg (Se debe consumir entre 1.5 g y 2.5 g máximo de proteina por kilo para aumento de masa¡)
    prot_cal = prot * 4
    grasa = 1 * peso  # Ejemplo de gramos de grasa por kg (Se debe consumir entre 0.8 g y 2 g máximo de grasa por Kilo para aumento de masa)
    grasa_cal = grasa * 9
    carboh_cal = cal_objetivo - grasa_cal - prot_cal
    carboh = carboh_cal / 4

    return {
        'cal': cal,
        'cal_objetivo': cal_objetivo,
        'prot': prot,
        'prot_cal': prot_cal,
        'grasa': grasa,
        'grasa_cal': grasa_cal,
        'carboh': carboh,
        'carboh_cal': carboh_cal,
        'porc_prot': prot_cal / cal_objetivo * 100,
        'porc_grasa': grasa_cal / cal_objetivo * 100,
        'porc_carboh': carboh_cal / cal_objetivo * 100
    }

@bp.route('/')
@login_required
def index():
    db, c = get_db()
    usuario_id = g.usuario['id']

    # Obtener datos del perfil
    c.execute('SELECT * FROM perfil_usuario WHERE usuario_id = %s', (usuario_id,))
    perfil = c.fetchone()

    # Obtener todas las medidas registradas
    c.execute('SELECT * FROM medidas WHERE usuario_id = %s ORDER BY fecha_medicion DESC', (usuario_id,))
    medidas = c.fetchall()

    #Calcular macros si el perfil está disponible
    macros = None
    if perfil:
        macros = calcular_macros(
            peso=perfil['peso_inicial'],
            genero=perfil['sexo'],
            objetivo=perfil['objetivo'],
            porcentaje=20  # Ejemplo de porcentaje para aumentar o bajar (Para aumentar o bajar de peso debe consumir o disminuir entre un 10% minimo a un 20% maximo de calorías)
        )

    return render_template('fittrack/index.html', perfil=perfil, medidas=medidas, macros=macros)

@bp.route('/medidas', methods=('GET', 'POST'))
@login_required
def medidas():
    if request.method == 'POST':
        peso = request.form['peso']
        cintura = request.form['cintura']
        pecho = request.form['pecho']
        cadera = request.form['cadera']
        brazo = request.form['brazo']
        pierna = request.form['pierna']
        error = None

        if not peso:
            error = 'Peso es requerido.'

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'INSERT INTO medidas (usuario_id, peso, cintura, pecho, cadera, brazo, pierna) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (g.usuario['id'], peso, cintura, pecho, cadera, brazo, pierna)
            )
            db.commit()
            return redirect(url_for('fittrack.index'))

    return render_template('fittrack/medidas.html')

@bp.route('/medidas/<int:id>/editar', methods=('GET', 'POST'))
@login_required
def editar_medidas(id):
    db, c = get_db()
    c.execute('SELECT * FROM medidas WHERE id = %s AND usuario_id = %s', (id, g.usuario['id']))
    medida = c.fetchone()

    if medida is None:
        abort(404, "Medida id {0} no existe.".format(id))

    if request.method == 'POST':
        peso = request.form['peso']
        cintura = request.form['cintura']
        pecho = request.form['pecho']
        cadera = request.form['cadera']
        brazo = request.form['brazo']
        pierna = request.form['pierna']
        error = None

        if not peso:
            error = 'Peso is required.'

        if error is None:
            c.execute(
                'UPDATE medidas SET peso = %s, cintura = %s, pecho = %s, cadera = %s, brazo = %s, pierna = %s WHERE id = %s AND usuario_id = %s',
                (peso, cintura, pecho, cadera, brazo, pierna, id, g.usuario['id'])
            )
            db.commit()
            return redirect(url_for('fittrack.index'))

        flash(error)

    return render_template('fittrack/editar_medidas.html', medida=medida)

@bp.route('/medidas/<int:id>/eliminar', methods=('POST',))
@login_required
def eliminar_medidas(id):
    db, c = get_db()
    c.execute('DELETE FROM medidas WHERE id = %s AND usuario_id = %s', (id, g.usuario['id']))
    db.commit()
    return redirect(url_for('fittrack.index'))