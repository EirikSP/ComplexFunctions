#version 430

#define point_count 1;
float pi = 3.14;

uniform float scale = 1.0;
uniform int count;
uniform float zoom = 3.0;

layout(local_size_x=point_count) in;

struct Point
{
    vec2 xy;
};


layout(std430, binding=0) buffer points_in
{
    Point points[];
} In;
layout(std430, binding=1) buffer points_out
{
    Point points[];
} Out;



vec2 pow_eul(vec2 z, float expon){
    return vec2(pow(z.x, expon), z.y*expon);
}

vec2 eul_to_euc(vec2 eul){
    return vec2(cos(eul.y)*eul.x, sin(eul.y)*eul.x);
}

vec2 euc_to_eul(vec2 euc){
    float angle = 2.0*atan(euc.y/(euc.x + length(euc)));
    while(angle > 2.0*pi){
        angle -= 2.0*pi;
    }
    return vec2(length(euc), angle);
}

vec2 conjugate_euc(vec2 z){
    return vec2(z.x, -z.y);
}


vec2 mult_euc(vec2 z1, vec2 z2){
    return vec2(z1.x*z2.x - z1.y*z2.y, z1.x*z2.y + z1.y*z2.x);
}

vec2 inverse_euc(vec2 z_euc){
    vec2 z_eul = euc_to_eul(z_euc);
    return eul_to_euc(vec2(1.0/z_eul.x, -z_eul.y));
}

vec2 exp_comp_eul(float base, vec2 z){
    return eul_to_euc(vec2(pow(base, z.x), z.y));
}

vec2 pow_euc(vec2 z, float expon){
    return eul_to_euc(pow_eul(euc_to_eul(z), expon));
}

vec2 divide_euc(vec2 z1, vec2 z2){
    return (mult_euc(z1, conjugate_euc(z2))/length(z2));
}




vec2 transform(vec2 xy){
    float a = 2;
    float d = 3;
    float b = 5;
    float c = 1;
    return divide_euc(a*xy*scale + vec2(b, 0.0), c*xy + vec2(d, 0.0));

    return pow_euc(xy, scale);
    return exp_comp_eul(scale, xy);
    return inverse_euc(xy*scale);
}


void main()
{
    int x = int(gl_GlobalInvocationID);
    if(x >= count){return;}

    Point in_point = In.points[x];

    vec2 xy = in_point.xy*zoom;

    vec2 out_xy = transform(xy);

    Point out_point;

    out_point.xy = out_xy/zoom;


    Out.points[x] = out_point;
}