import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST() {
  try {
    // Run the python script to reset database and seed a new demo incident
    // Assuming backend is one directory up
    const { stdout, stderr } = await execAsync('cd ../backend && .venv/bin/python scripts/seed_demo.py');
    console.log('Seed stdout:', stdout);
    if (stderr) console.error('Seed stderr:', stderr);

    return NextResponse.json({ success: true, message: 'Demo seeded successfully' });
  } catch (error) {
    console.error('Error running demo script:', error);
    // If the virtualenv path is different or we are running locally without one, fallback:
    try {
      const { stdout } = await execAsync('cd ../backend && python scripts/seed_demo.py');
      console.log('Fallback stdout:', stdout);
      return NextResponse.json({ success: true, message: 'Demo seeded successfully via fallback' });
    } catch (e) {
      console.error('Fallback failed:', e);
      return NextResponse.json(
        { success: false, error: 'Failed to run demo seed script' },
        { status: 500 }
      );
    }
  }
}
