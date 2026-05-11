// Animated mesh canvas
const canvas = document.createElement('canvas');
canvas.id = 'meshCanvas';
document.body.prepend(canvas);

const ctx = canvas.getContext('2d');
let w, h, particles = [];

let mouse = {
    x: null,
    y: null,
    radius: 150
};

window.addEventListener('mousemove', function(event) {
    mouse.x = event.x;
    mouse.y = event.y;
});

window.addEventListener('mouseout', function() {
    mouse.x = null;
    mouse.y = null;
});

function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

for (let i = 0; i < 80; i++) {
    particles.push({
        x: Math.random() * w, 
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.5, 
        vy: (Math.random() - 0.5) * 0.5,
        r: Math.random() * 2 + 1
    });
}

let animationFrameId;

function draw() {
    ctx.clearRect(0, 0, w, h);
    
    for (let i = 0; i < particles.length; i++) {
        let p = particles[i];
        
        p.x += p.vx; 
        p.y += p.vy;
        
        if (p.x < 0 || p.x > w) p.vx *= -1;
        if (p.y < 0 || p.y > h) p.vy *= -1;

        if (mouse.x !== null && mouse.y !== null) {
            let dx = p.x - mouse.x;
            let dy = p.y - mouse.y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < mouse.radius) {
                let force = (mouse.radius - distance) / mouse.radius;
                p.x += (dx / distance) * force * 2;
                p.y += (dy / distance) * force * 2;
            }
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(168, 85, 247, 0.5)';
        ctx.fill();

        for (let j = i + 1; j < particles.length; j++) {
            let q = particles[j];
            let dx = p.x - q.x;
            let dy = p.y - q.y;
            let distSq = dx * dx + dy * dy;
            
            if (distSq < 150 * 150) {
                let dist = Math.sqrt(distSq);
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(q.x, q.y);
                ctx.strokeStyle = `rgba(6, 182, 212, ${0.1 * (1 - dist / 150)})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        }
        
        if (mouse.x !== null && mouse.y !== null) {
            let dx = p.x - mouse.x;
            let dy = p.y - mouse.y;
            let distSq = dx * dx + dy * dy;
            if (distSq < 200 * 200) {
                let dist = Math.sqrt(distSq);
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(mouse.x, mouse.y);
                ctx.strokeStyle = `rgba(168, 85, 247, ${0.15 * (1 - dist / 200)})`;
                ctx.lineWidth = 0.8;
                ctx.stroke();
            }
        }
    }
    animationFrameId = requestAnimationFrame(draw);
}

draw();
