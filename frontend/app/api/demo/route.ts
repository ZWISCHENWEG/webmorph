import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST() {
  try {
    // Use uv run to ensure the virtual environment and dependencies are correctly loaded
    const { stdout, stderr } = await execAsync('cd ../backend && uv run scripts/seed_demo.py --reset');
    console.log('Seed stdout:', stdout);
    if (stderr) console.error('Seed stderr:', stderr);

    return NextResponse.json({ success: true, message: 'Demo seeded successfully' });
  } catch (error) {
    console.error('Error running demo script:', error);
    // If uv isn't available globally, try using the direct venv python
    try {
      const { stdout } = await execAsync('cd ../backend && .venv/bin/python scripts/seed_demo.py --reset');
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
