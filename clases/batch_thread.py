import os
import time
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from PyQt6 import QtCore
from clases.utils import parse_info_file, parse_resta_name

class BatchThread(QtCore.QThread):
    progress_signal = QtCore.pyqtSignal(str)
    folder_done_signal = QtCore.pyqtSignal(int)
    all_done_signal = QtCore.pyqtSignal()
    simulation_result_signal = QtCore.pyqtSignal(object)

    def __init__(self, base_folder, subfolders, parent=None):
        super().__init__(parent)
        self.base_folder = base_folder
        self.subfolders = subfolders
        self.stop_requested = False

        # Para ETA: contaremos cuántos "a" en total hay
        self.total_iterations = 0
        self.done_iterations = 0

    def request_stop(self):
        self.stop_requested = True

    def countTotalIterations(self):
        """
        Hace un primer pase para sumar el total de a_values
        en todas las subcarpetas, para calcular ETA.
        """
        total = 0
        for folder_name in self.subfolders:
            info_path = os.path.join(self.base_folder, folder_name, "info.txt")
            if not os.path.exists(info_path):
                continue
            try:
                resta_name, a_start, a_stop, a_step, eq_code, init_values = parse_info_file(info_path)
                if a_start is not None:
                    # Reanudación: si hay log.csv, podríamos omitir
                    # Pero para simplificar, asumimos que contaremos
                    # todo el rango
                    a_values = np.arange(a_start, a_stop, a_step)
                    total += len(a_values)
            except:
                pass
        return total

    def run(self):
        # Contar total de iteraciones
        self.total_iterations = self.countTotalIterations()
        self.done_iterations = 0

        start_time = time.time()

        total_sub = len(self.subfolders)
        for idx, folder_name in enumerate(self.subfolders):
            if self.stop_requested:
                self.progress_signal.emit("Proceso detenido por el usuario.")
                break

            subdir = os.path.join(self.base_folder, folder_name)
            self.progress_signal.emit(f"[{idx+1}/{total_sub}] Procesando subcarpeta '{folder_name}'...")

            info_path = os.path.join(subdir, "info.txt")
            if not os.path.exists(info_path):
                self.progress_signal.emit(f"No existe info.txt en {folder_name}, se omite.")
                self.folder_done_signal.emit(idx)
                continue

            try:
                resta_name, a_start, a_stop, a_step, eq_code, init_values = parse_info_file(info_path)
            except Exception as e:
                self.progress_signal.emit(f"Error parseando info.txt: {e}")
                self.folder_done_signal.emit(idx)
                continue

            # "Compilar" eq_code
            local_vars = {}
            try:
                exec(eq_code, {"np": np}, local_vars)
                sistema_dinamico = local_vars['sistema_dinamico']
            except Exception as e:
                self.progress_signal.emit(f"Error generando ecuación en {folder_name}: {e}")
                self.folder_done_signal.emit(idx)
                continue

            # Reanudación
            log_path = os.path.join(subdir, "log.csv")
            a_ultimo = None
            if os.path.exists(log_path):
                df_log = pd.read_csv(log_path)
                if not df_log.empty:
                    a_ultimo = df_log['a'].max()

            if (a_ultimo is not None) and (a_ultimo < a_stop):
                a_inicial = a_ultimo + a_step
            else:
                a_inicial = a_start

            a_values = np.arange(a_inicial, a_stop, a_step)
            if len(a_values)==0:
                self.progress_signal.emit(f"{folder_name} ya completo o sin rango.")
                self.folder_done_signal.emit(idx)
                continue

            idxA, idxB = parse_resta_name(resta_name)
            df_new = []
            t_span = (0, 310)
            t_eval = np.linspace(0, 310, 1000)

            for a_val in a_values:
                if self.stop_requested:
                    self.progress_signal.emit("Proceso detenido en mitad de iteración.")
                    break

                # solve_ivp
                try:
                    sol = solve_ivp(sistema_dinamico, t_span, init_values, args=(a_val,), t_eval=t_eval)
                    if sol.success:
                        self.simulation_result_signal.emit(sol)
                except Exception as e:
                    self.progress_signal.emit(f"Error solve_ivp a={a_val} en {folder_name}: {e}")
                    break

                varA_values = sol.y[idxA]
                varB_values = sol.y[idxB]
                t_values = sol.t

                def varA_interp(t_):
                    return np.interp(t_, t_values, varA_values)
                def varB_interp(t_):
                    return np.interp(t_, t_values, varB_values)
                def abs_diff(t_):
                    return abs(varA_interp(t_) - varB_interp(t_))

                # Sub-intervalos [200..300]
                for i_time in range(200, 300):
                    if self.stop_requested:
                        break
                    try:
                        res = minimize_scalar(lambda tau: -abs_diff(tau),
                                              bounds=(i_time, i_time+1),
                                              method='bounded')
                        max_val = -res.fun
                        df_new.append({'a': a_val, 'max_value': max_val})
                    except Exception as e:
                        self.progress_signal.emit(f"Error optimizando i={i_time} a={a_val} en {folder_name}: {e}")
                        continue

                # Actualizar iteración y ETA
                self.done_iterations += 1
                elapsed = time.time() - start_time
                speed = self.done_iterations / elapsed  # iteraciones por segundo
                remaining = self.total_iterations - self.done_iterations
                eta = remaining / speed if speed>0 else 0

                self.progress_signal.emit(
                    f"Subcarpeta={folder_name}, Resta={resta_name}, "
                    f"a={a_val:.3f}, Iter={self.done_iterations}/{self.total_iterations}, "
                    f"ETA={eta:.1f}s"
                )

                if self.stop_requested:
                    break

            if df_new:
                df_new = pd.DataFrame(df_new)
                mode = 'a' if os.path.exists(log_path) else 'w'
                header = (mode=='w')
                df_new.to_csv(log_path, mode=mode, header=header, index=False)

            self.folder_done_signal.emit(idx)

        self.all_done_signal.emit()
