import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

file_url = 'file:///' + os.path.abspath('dist_online/index.html').replace('\\', '/')
print('Testing URL:', file_url)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    errors = []
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.on('pageerror', lambda err: errors.append(str(err)))

    page.goto(file_url, wait_until='domcontentloaded')
    
    # 1. Check gate is visible
    gate = page.locator('#pgePasswordGateOverlay')
    assert gate.is_visible(), 'Gate should be visible on first load'
    print('PASS 1: Gate is initially visible.')

    # 2. Enter incorrect password
    input_box = page.locator('#pgeAccessPasswordInput')
    btn = page.locator('#btnSubmitPgeAccess')
    input_box.fill('wrongpassword')
    btn.click()
    page.wait_for_timeout(500)
    err_msg = page.locator('#pgeAccessErrorMsg')
    assert err_msg.is_visible(), 'Error message should be visible on wrong password'
    print('PASS 2: Wrong password triggers error message.')

    # 3. Enter correct password ('yogaktauk')
    input_box.fill('yogaktauk')
    btn.click()
    page.wait_for_timeout(600)
    assert not gate.is_visible(), 'Gate should be hidden after correct password'
    print('PASS 3: Correct password unlocks dashboard.')

    # 4. Simulate 16 minutes of inactivity
    sixteen_mins_ago = page.evaluate('''() => {
        const past = Date.now() - (16 * 60 * 1000);
        sessionStorage.setItem("pge_last_activity_ts", String(past));
        return past;
    }''')
    print('Simulated past timestamp:', sixteen_mins_ago)
    
    # Trigger visibility change to trigger the lock
    page.evaluate('() => { document.dispatchEvent(new Event("visibilitychange")); }')
    page.wait_for_timeout(500)
    
    assert gate.is_visible(), 'Gate should be locked again after 16 mins of inactivity'
    badge_text = page.locator('#pgeGateSubtitle').inner_text()
    print('Lock banner text:', badge_text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
    assert '15 menit' in badge_text, 'Badge should mention 15 menit'
    print('PASS 4: 15-minute inactivity triggers automatic session lock.')

    # 5. Re-authenticate
    input_box.fill('yogaktauk')
    btn.click()
    page.wait_for_timeout(600)
    assert not gate.is_visible(), 'Gate should unlock again after re-entering password'
    print('PASS 5: Re-authentication works cleanly.')

    # 6. Test direct timer expiry by setting timeout function
    page.evaluate('() => { lockDashboardSession("Sesi terkunci otomatis karena tidak aktif selama 15 menit."); }')
    page.wait_for_timeout(500)
    assert gate.is_visible(), 'Lock function should display overlay'
    print('PASS 6: lockDashboardSession works reliably.')

    print('Console errors count:', len(errors))
    if errors:
        print('Sample errors:', errors[:5])
    
    # Take screenshot of the locked state
    os.makedirs('scratch', exist_ok=True)
    page.screenshot(path='scratch/session_locked_15min.png')
    print('Saved screenshot to scratch/session_locked_15min.png')

    browser.close()

print('ALL INACTIVITY AND SECURITY TESTS PASSED!')
