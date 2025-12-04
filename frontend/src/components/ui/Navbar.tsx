'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Disclosure, Menu, Transition } from '@headlessui/react';
import { Bars3Icon, XMarkIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { Fragment } from 'react';
import clsx from 'clsx';
import { useAuth } from '@/contexts/AuthContext';

const navigation = [
  { name: 'Home', href: '/' },
  { name: 'Decks', href: '/decks' },
  { name: 'Cards', href: '/cards' },
  { name: 'Videos', href: '/videos' },
  { name: 'Matches', href: '/matches' },
  { name: 'Tournaments', href: '/tournaments' },
  { name: 'Coach', href: '/coaching' },
  { name: 'Meta', href: '/meta' },
  { name: 'Channels', href: '/channels' },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout, isLoading } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <Disclosure as="nav" className="bg-white shadow-sm border-b border-gray-200">
      {({ open }) => (
        <>
          <div className="container mx-auto px-4">
            <div className="flex h-16 justify-between">
              <div className="flex">
                <Link href="/" className="flex items-center">
                  <span className="text-xl font-bold text-pokemon-red">TCG</span>
                  <span className="text-xl font-bold text-pokemon-blue ml-1">Platform</span>
                </Link>
                <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={clsx(
                        'inline-flex items-center px-3 py-2 text-sm font-medium rounded-md',
                        pathname === item.href
                          ? 'bg-gray-100 text-pokemon-blue'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      )}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              </div>

              {/* User Menu */}
              <div className="hidden sm:flex sm:items-center">
                {isLoading ? (
                  <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse" />
                ) : isAuthenticated ? (
                  <Menu as="div" className="relative">
                    <Menu.Button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100">
                      <UserCircleIcon className="h-6 w-6" />
                      <span>{user?.display_name || user?.username}</span>
                    </Menu.Button>
                    <Transition
                      as={Fragment}
                      enter="transition ease-out duration-100"
                      enterFrom="transform opacity-0 scale-95"
                      enterTo="transform opacity-100 scale-100"
                      leave="transition ease-in duration-75"
                      leaveFrom="transform opacity-100 scale-100"
                      leaveTo="transform opacity-0 scale-95"
                    >
                      <Menu.Items className="absolute right-0 mt-2 w-48 origin-top-right bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                        <div className="py-1">
                          <Menu.Item>
                            {({ active }) => (
                              <Link
                                href="/profile"
                                className={clsx(
                                  'block px-4 py-2 text-sm',
                                  active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                                )}
                              >
                                Profile
                              </Link>
                            )}
                          </Menu.Item>
                          <Menu.Item>
                            {({ active }) => (
                              <button
                                onClick={handleLogout}
                                className={clsx(
                                  'block w-full text-left px-4 py-2 text-sm',
                                  active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                                )}
                              >
                                Sign Out
                              </button>
                            )}
                          </Menu.Item>
                        </div>
                      </Menu.Items>
                    </Transition>
                  </Menu>
                ) : (
                  <div className="flex items-center gap-2">
                    <Link
                      href="/login"
                      className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
                    >
                      Sign In
                    </Link>
                    <Link
                      href="/register"
                      className="px-4 py-2 text-sm font-medium text-white bg-pokemon-blue rounded-lg hover:bg-blue-700"
                    >
                      Sign Up
                    </Link>
                  </div>
                )}
              </div>

              {/* Mobile menu button */}
              <div className="flex items-center sm:hidden">
                <Disclosure.Button className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-500">
                  <span className="sr-only">Open main menu</span>
                  {open ? (
                    <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                  ) : (
                    <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                  )}
                </Disclosure.Button>
              </div>
            </div>
          </div>

          {/* Mobile menu */}
          <Disclosure.Panel className="sm:hidden">
            <div className="space-y-1 px-4 pb-3 pt-2">
              {navigation.map((item) => (
                <Disclosure.Button
                  key={item.name}
                  as={Link}
                  href={item.href}
                  className={clsx(
                    'block px-3 py-2 text-base font-medium rounded-md',
                    pathname === item.href
                      ? 'bg-gray-100 text-pokemon-blue'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  {item.name}
                </Disclosure.Button>
              ))}

              {/* Mobile Auth Links */}
              <div className="border-t border-gray-200 pt-4 mt-4">
                {isAuthenticated ? (
                  <>
                    <div className="px-3 py-2 text-sm text-gray-500">
                      Signed in as {user?.username}
                    </div>
                    <Disclosure.Button
                      as={Link}
                      href="/profile"
                      className="block px-3 py-2 text-base font-medium text-gray-600 rounded-md hover:bg-gray-50"
                    >
                      Profile
                    </Disclosure.Button>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-3 py-2 text-base font-medium text-gray-600 rounded-md hover:bg-gray-50"
                    >
                      Sign Out
                    </button>
                  </>
                ) : (
                  <>
                    <Disclosure.Button
                      as={Link}
                      href="/login"
                      className="block px-3 py-2 text-base font-medium text-gray-600 rounded-md hover:bg-gray-50"
                    >
                      Sign In
                    </Disclosure.Button>
                    <Disclosure.Button
                      as={Link}
                      href="/register"
                      className="block px-3 py-2 text-base font-medium text-pokemon-blue rounded-md hover:bg-gray-50"
                    >
                      Sign Up
                    </Disclosure.Button>
                  </>
                )}
              </div>
            </div>
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}
