from math import fabs
import math
import moderngl_window as mglw
from moderngl_window import geometry
from numpy import pi
import numpy as np
import imgui
import moderngl_window.integrations.imgui as img


class App(mglw.WindowConfig):
    window_size = 900, 900
    resource_dir = "ComplexFunctions"
    vsync = False
    gl_version = (4, 3)
    aspect_ratio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        imgui.create_context()
        self.imgui = img.ModernglWindowRenderer(self.wnd)

        """
        Data Strucure 2f position, 2f velocity 1f weight
        -1.0 < Position < 1.0
        """
        self.scale = 1.0
        self.zoom = 3.0
        self.lines = 16
        self.old_lines = 16
        self.old_zoom = self.zoom

        #self.particles = np.array([-0.3, -0.5, 0.1, 0.0, 1.0, 0.5, -0.3, 0.0,0.1, 1.0, 0.0, 0.6, 0.0, -0.1, 1.0]).astype('f4')
        self.points = self.generate_points(20000, 16).astype('f4')

        self.point_count = self.points.shape[0]
        self.local_size = 1024
        self.group_size = int(math.ceil(self.point_count / self.local_size))

        self.point_buffer_1 = self.ctx.buffer(data=self.points)
        self.point_buffer_2 = self.ctx.buffer(data=self.points)


        self.render_program_grid = self.load_program(vertex_shader='vertex_shader.glsl', fragment_shader='fragment_shader.glsl')
        self.render_program_transformed = self.load_program(vertex_shader='vertex_shader.glsl', fragment_shader='fragment_shader_transformed.glsl')

        self.transformer = self.load_compute_shader('transform.glsl', {'point_count':self.local_size})
        self.transformer['count'] = self.point_count


        self.vertex_render_grid = self.ctx.vertex_array(self.render_program_grid, [(self.point_buffer_1, '2f4', 'in_vert')])
        self.vertex_render_transformed = self.ctx.vertex_array(self.render_program_transformed, [(self.point_buffer_2, '2f4', 'in_vert')])

        #self.transformer['pi'] = 3.14

    
    def generate_points(self, N, lines):
        x_lines_y = np.linspace(-0, 1, N, endpoint=False)
        x_lines_x = np.linspace(-1, 1, lines, endpoint=False)

        y_lines_y = np.linspace(-0, 1, lines, endpoint=False)
        y_lines_x = np.linspace(-1, 1, N, endpoint=False)

        x_lines = np.array(np.meshgrid(x_lines_x, x_lines_y)).T.reshape(-1, 2)

        y_lines = np.array(np.meshgrid(y_lines_x, y_lines_y)).T.reshape(-1, 2)
        return np.concatenate([x_lines, y_lines], axis=0)


        



    def render(self, time: float, frame_time: float):
        self.ctx.clear()

        self.point_buffer_1.bind_to_storage_buffer(0)
        self.point_buffer_2.bind_to_storage_buffer(1)
        
        
        self.transformer.run(group_x=self.group_size)
    
        self.vertex_render_grid.render(self.ctx.POINTS)
        self.vertex_render_transformed.render(self.ctx.POINTS)

        self.render_ui()

    def generate_grid(self, lines):
        self.points = self.generate_points(20000, lines).astype('f4')

        self.point_count = self.points.shape[0]
        self.group_size = int(math.ceil(self.point_count / self.local_size))

        self.point_buffer_1 = self.ctx.buffer(data=self.points)
        self.point_buffer_2 = self.ctx.buffer(data=self.points)

        self.transformer['count'] = self.point_count


        self.vertex_render_grid = self.ctx.vertex_array(self.render_program_grid, [(self.point_buffer_1, '2f4', 'in_vert')])
        self.vertex_render_transformed = self.ctx.vertex_array(self.render_program_transformed, [(self.point_buffer_2, '2f4', 'in_vert')])


    def update_uniforms(self):
        self.transformer['scale'] = self.scale
        self.transformer['zoom'] = self.zoom
        
        if self.lines != self.old_lines:
            
            self.generate_grid(self.lines)
            self.old_lines = self.lines





    def render_ui(self):
        imgui.new_frame()

        if imgui.begin("Settings"):
            imgui.push_item_width(imgui.get_window_width()*0.5)

            changed = False
            c, self.scale = imgui.slider_float(
                "Real", self.scale, -4.0, 4.0
            )
            changed = changed or c
            c, self.zoom = imgui.slider_float(
                "Zoom", self.zoom,  0.01, 10.0
            )
            changed = changed or c
            c, self.lines = imgui.slider_int(
                "Grid Lines", self.lines,  2, 30
            )
            changed = changed or c
            if changed:
                self.update_uniforms()
            
            
            imgui.pop_item_width()



        imgui.end()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)




if __name__=='__main__':
    mglw.run_window_config(App)