void main () {
    // Previously, you'd have rendered your complete scene into a texture
    // bound to "fullScreenTexture."
    vec4 rValue = texture2D(fullscreenTexture, gl_TexCoords[0] - rOffset);
    vec4 gValue = texture2D(fullscreenTexture, gl_TexCoords[0] - gOffset);
    vec4 bValue = texture2D(fullscreenTexture, gl_TexCoords[0] - bOffset);

    // Combine the offset colors.
    gl_FragColor = vec4(rValue.r, gValue.g, bValue.b, 1.0);
}